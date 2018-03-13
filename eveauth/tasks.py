import json
import requests

from datetime import timedelta

from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth.models import User
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.utils.timezone import now

from avrseauth.settings import members, blues
from avrseauth.celery import app

from sde.models import System, Station, Type

from eveauth import ipb
from eveauth.models.alliance import Alliance
from eveauth.models.asset import Asset
from eveauth.models.character import Character
from eveauth.models.corporation import Corporation
from eveauth.models.clone import Clone, CloneImplant
from eveauth.models.implant import Implant
from eveauth.models.kill import Kill
from eveauth.models.templink import Templink
from eveauth.models.skill import Skill
from eveauth.models.structure import Structure, Service
from eveauth.models.role import Role
from eveauth.esi import ESI, parse_api_date
from eveauth.discord.api import DiscordAPI, is_bot_active

from timerboard.models import Timer


def get_server():
    import Ice
    Ice.loadSlice( '', ['-I' + Ice.getSliceDir(), "eveauth/Murmur.ice"])
    import Murmur

    ice = Ice.initialize()
    meta = Murmur.MetaPrx.checkedCast(ice.stringToProxy('Meta:tcp -h 127.0.0.1 -p 6502'))
    server = meta.getServer(1)
    return server


# Update user groups from the API
@app.task(name="spawn_groupupdates")
def spawn_groupupdates():
    users = User.objects.all()
    for user in users:
        update_groups.delay(user.id)

    print "Spawned group update tasks for %s users" % users.count()
    return users.count()


# Update location for characters with tokens
@app.task(name="spawn_character_location_updates")
def spawn_character_location_updates():
    chars = Character.objects.filter(
        token__isnull=False
    ).all()
    for char in chars:
        update_character_location.delay(char.id)

    print "Spawned character location update tasks for %s chars" % chars.count()


# Update data on all corporations with director tokens
@app.task(name="spawn_corporation_updates")
def spawn_corporation_updates():
    corps = Corporation.objects.filter(
        characters__token__isnull=False,
        characters__roles__name="director"
    ).distinct()
    for corp in corps:
        update_corporation.delay(corp.id)


# Set expired templinks inactive and kick anyone using them from mumble
@app.task(name="purge_expired_templinks")
def purge_expired_templinks():
    templinks = Templink.objects.filter(
        active=True,
        expires__lt=timezone.now()
    ).all()

    for templink in templinks:
        templink.active = False
        templink.save()

        purge_templink_users.delay(templink.id, reason="Templink expired")

        print "Purged templink [%s] %s" % (templink.tag, templink.link)


# Move people to mumble
@app.task(name="mumble_afk_check")
def mumble_afk_check():
    if settings.MUMBLE_AUTO_AFK:
        server = get_server()
        users = server.getUsers().items()

        for session, user in users:
            if (user.selfDeaf and user.idlesecs >= settings.MUMBLE_AUTO_AFK_DELAY) or user.idlesecs >= 7200:
                if user.channel != settings.MUMBLE_AUTO_AFK_CHANNEL:
                    # Move the user to the afk channel
                    user.channel = settings.MUMBLE_AUTO_AFK_CHANNEL
                    server.setState(user)

        server.ice_getCommunicator().destroy()



# Purge all users using a particular templink
@app.task(name="purge_templink_users")
def purge_templink_users(templink_id, reason="Templink deactivated"):
    server = get_server()

    # Get templink user list
    templink = Templink.objects.get(id=templink_id)
    id_map = map(lambda x: x.mumble_id(), templink.users.all())

    # Get active user list from server
    users = server.getUsers().items()

    # Get a list of active users using this temp link
    user_map = filter(lambda x: x.userid in id_map, map(lambda x: x[1], users))

    # Kick each user from the server
    for user in user_map:
        server.kickUser(user.session, reason)

    server.ice_getCommunicator().destroy()


# Update all corp data from the first available director API
@app.task(name="update_corporation")
def update_corporation(corp_id):
    # Look for character with the right roles
    corp = Corporation.objects.get(id=corp_id)
    director = corp.characters.filter(
        roles__name="director",
        token__isnull=False
    ).first()

    if director != None:
        api = ESI(director.token)

        # Structures
        structures = api.get("/v2/corporations/%s/structures/" % corp.id)
        corp.structures.exclude(
            id__in=map(
                lambda x: x['structure_id'],
                structures
            )
        ).delete()

        for structure in structures:
            with transaction.atomic():
                db_structure = Structure.objects.filter(id=structure['structure_id']).first()
                if db_structure == None:
                    db_structure = Structure(id=structure['structure_id'])

                previous_state = db_structure.state

                db_structure.corporation = corp
                db_structure.type_id = structure['type_id']
                db_structure.station = Station.get_or_create(structure['structure_id'], api)
                db_structure.system_id = structure['system_id']
                db_structure.profile_id = structure['profile_id']
                db_structure.state = structure['state']
                db_structure.reinforce_weekday = structure['reinforce_weekday']
                db_structure.reinforce_hour = structure['reinforce_hour']

                if "fuel_expires" in structure:
                    db_structure.fuel_expires = parse_api_date(structure['fuel_expires'])
                else:
                    db_structure.fuel_expires = None
                
                if "state_timer_start" in structure:
                    db_structure.state_timer_start = parse_api_date(structure['state_timer_start'])
                else:
                    db_structure.state_timer_start = None

                if "state_timer_end" in structure:
                    db_structure.state_timer_end = parse_api_date(structure['state_timer_end'])
                else:
                    db_structure.state_timer_end = None
                db_structure.save()

                db_structure.services.all().delete()
                if "services" in structure:
                    for service in structure['services']:
                        Service(
                            structure=db_structure,
                            name=service['name'],
                            state={'online': True, 'offline': False}[service['state']]
                        ).save()

                # Create timer if this is newly reinforced
                if previous_state != structure['state']:
                    if "reinforce" in structure['state'] or structure['state'] == "anchoring":
                        timer = Timer(
                            structure_id=structure['type_id'],
                            name=db_structure.station.name.replace("%s - " % db_structure.system.name, ""),
                            owner=corp.ticker,
                            side=0,
                            system_id=structure['system_id'],
                            date=db_structure.state_timer_end,
                            stage={"armor_reinforce": "AR", "hull_reinforce": "ST", "anchoring": "AN"}[structure['state']],
                            visible_to_level=2,
                            created_by=User.objects.first(),
                            generated=True
                        )
                        timer.save()

                        # CODE TO PING ON DISCORD GOES HERE 

        print "Updated all info for Corporation %s" % corp.name


# Update a users groups from the API
@app.task(name="update_groups")
def update_groups(user_id):
    user = User.objects.get(id=user_id)
    print "Updating groups for %s" % user.username
    social = user.social_auth.filter(provider="eveonline").first()

    # Queue character updates
    for char in user.characters.all():
        update_character.delay(char.id)

    # Update char/corp/alliance
    api = ESI()
    char_id = social.extra_data['id']
    char = api.get("/v4/characters/%s/" % char_id)

    user.profile.character = Character.get_or_create(char_id)
    user.profile.corporation = Corporation.get_or_create(char['corporation_id'])
    if "alliance_id" in char:
        user.profile.alliance = Alliance.get_or_create(char['alliance_id'])
    else:
        user.profile.alliance = None


    # Update groups
    for group in user.groups.filter(name__startswith="Corp: ").all():
        user.groups.remove(group)
    for group in user.groups.filter(name__startswith="Alliance: ").all():
        user.groups.remove(group)

    if user.profile.corporation != None:
        user.groups.add(user.profile.corporation.group)
    if user.profile.alliance != None:
        user.groups.add(user.profile.alliance.group)


    # Update access level
    char_id = user.profile.character_id
    corp_id = user.profile.corporation_id
    alliance_id = user.profile.alliance_id

    if corp_id in members['corps'] or alliance_id in members['alliances'] or char_id in members['chars']:
        user.profile.level = 2
    elif corp_id in blues['corps'] or alliance_id in blues['alliances'] or char_id in members['chars']:
        user.profile.level = 1
    else:
        user.profile.level = 0

    user.profile.save()

    # Update IPB User
    if ipb.is_active():
        if user.profile.forum_id:
            forum_api = ipb.IPBUser(user)
            forum_api.update_access_level()

    update_discord.delay(user.id)


# Update Discord status
@app.task(name="update_discord")
def update_discord(user_id):
    if not is_bot_active():
        return

    user = User.objects.get(id=user_id)
    print "Updating discord for %s" % user.username

    social_discord = user.social_auth.filter(provider="discord").first()
    if social_discord != None:
        api = DiscordAPI()

        # Check if the user is on discord
        if api.is_user_in_guild(social_discord.uid):
            # Check if we should kick the user
            if user.profile.level < settings.DISCORD_ACCESS_LEVEL:
                api.kick_member(social_discord.uid)
                return

            # Update the users name
            api.set_name(social_discord.uid, user.profile.character.name)

            # Update the users roles
            roles = [
                user.profile.corporation.ticker,
                ["Non-member", "Blue", "Member"][user.profile.level]
            ]
            groups = user.groups.exclude(
                Q(name__startswith="Corp: ") | Q(name__startswith="Alliance: ")
            ).all()
            for group in groups:
                roles.append(group.name)
            print "Updating roles: %s" % str(roles)
            api.update_roles(social_discord.uid, roles)


@app.task(name="update_character")
def update_character(character_id):
    # Get the db objects we need
    db_char = Character.objects.get(id=character_id)

    # Grab public info from API
    api = ESI()
    char = api.get("/v4/characters/%s/" % db_char.id)

    db_char.name = char['name']
    db_char.corp = Corporation.get_or_create(char['corporation_id'])
    if "alliance_id" in char:
        db_char.alliance = Alliance.get_or_create(char['alliance_id'])
    else:
        db_char.alliance = None
    db_char.save()

    # Grab non-public info
    if db_char.token != None:
        api = ESI(db_char.token)

        # Check refresh token to see if it's still valid
        if api._refresh_access_token() == False:
            # Check if we've had 24 within the last 72hrs failures. This runs hourly so that means EVE would need to be dead for a full day.
            cache_key = "fail_history_character_%s" % db_char.id
            fail_history = cache.get(cache_key, [])
            if len(fail_history) > 24:
                db_char.token.delete()
                db_char.owner = None
                db_char.token = None
                db_char.save()

                fail_history = []
            else:
                fail_history.append(now())

            cache.set(cache_key, fail_history, 259200)
            return

        # Wallet
        db_char.wallet = api.get("/v1/characters/$id/wallet/")

        # Location
        location = api.get("/v1/characters/$id/location/")
        db_char.system_id = location['solar_system_id']

        # Ship
        ship = api.get("/v1/characters/$id/ship/")
        db_char.ship_id = ship['ship_type_id']

        # Fatigue
        fatigue = api.get("/v1/characters/$id/fatigue/")
        if "jump_fatigue_expire_date" in fatigue:
            db_char.fatigue_expire_date = parse_api_date(fatigue['jump_fatigue_expire_date'])
            db_char.last_jump_date = parse_api_date(fatigue['last_jump_date'])

        # Roles
        with transaction.atomic():
            roles = api.get("/v2/characters/$id/roles/")
            db_char.roles.all().delete()

            if "roles" in roles:
                for role in roles['roles']:
                    Role(
                        character=db_char,
                        name=role
                    ).save()

        db_char.save()

        # Skills
        skills = api.get("/v4/characters/$id/skills/")
        with transaction.atomic():
            Skill.objects.filter(character=db_char).delete()
            for skill in skills['skills']:
                Skill(
                    character=db_char,
                    type_id=skill['skill_id'],
                    trained_skill_level=skill['trained_skill_level'],
                    active_skill_level=skill['active_skill_level'],
                    skillpoints_in_skill=skill['skillpoints_in_skill']
                ).save()

        # Assets
        with transaction.atomic():
            Asset.objects.filter(character=db_char).delete()

            page = 1
            while True:
                assets = api.get("/v3/characters/$id/assets/", get_vars={'page': page})
                if len(assets) < 1:
                    break

                for asset in assets:
                    db_asset = Asset(
                        character=db_char,
                        id=asset['item_id'],
                        type_id=asset['type_id'],
                        flag=asset['location_flag'],
                        quantity=asset['quantity'],
                        raw_quantity=asset['quantity'],
                        singleton=asset['is_singleton'],
                    )

                    if asset['location_flag'] == "Hangar":
                        station = Station.get_or_create(asset['location_id'], api)
                        db_asset.system = station.system
                    else:
                        db_asset.parent_id = asset['location_id']
                    db_asset.save()

                page = page + 1

            # Fetch names for all ships/containers
            items = list(
                Asset.objects.filter(
                    Q(character=db_char),
                    Q(type__group__category_id=6) | Q(type__group__in=[12 , 340, 448])
                ).values_list(
                    'id',
                    flat=True
                )
            )

            asset_names = api.post("/v1/characters/$id/assets/names/", data=json.dumps(items))
            for asset in asset_names:
                db_asset = Asset.objects.get(id=asset['item_id'])
                db_asset.name = asset['name']
                db_asset.save()

            # Fix systems
            db_assets = Asset.objects.filter(
                character=db_char,
                system__isnull=True
            ).all()
            for db_asset in db_assets:
                try:
                    if db_asset.parent != None:
                        db_asset.system = db_asset.parent.system
                except Asset.DoesNotExist:
                    pass
                    #print db_asset.parent_id
                db_asset.save()

        # Implants
        with transaction.atomic():
            implants = api.get("/v1/characters/$id/implants/")
            db_char.implants.all().delete()
            for implant in implants:
                Implant(
                    character=db_char,
                    type_id=implant
                ).save()

        # Clones
        info_sync = db_char.skills.filter(type_id=33399).first()
        if info_sync != None:
            info_sync = timedelta(hours=info_sync.trained_skill_level)
        else:
            info_sync = timedelta(hours=0)

        clones = api.get("/v3/characters/$id/clones/")
        db_char.home = Station.get_or_create(clones['home_location']['location_id'], api)
        if "last_clone_jump_date" in clones:
            db_char.clone_jump_ready = parse_api_date(clones['last_clone_jump_date']) - info_sync + timedelta(hours=24)
        db_char.save()

        db_char.clones.all().delete()
        for clone in clones['jump_clones']:
            if "name" in clone:
                name = clone['name']
            else:
                name = ""

            db_clone = Clone(
                id=clone['jump_clone_id'],
                character=db_char,
                name=name,
                location=Station.get_or_create(clone['location_id'], api)
            )
            db_clone.save()

            for implant in clone['implants']:
                CloneImplant(
                    clone=db_clone,
                    type_id=implant
                ).save()

        print "Updated all info for character %s" % db_char.name



@app.task(name="update_character_location")
def update_character_location(character_id):
    # Get the db objects we need
    db_char = Character.objects.get(id=character_id)
    api = ESI(db_char.token)

    # Location
    location = api.get("/v1/characters/$id/location/")
    db_char.system_id = location['solar_system_id']

    # Ship
    ship = api.get("/v1/characters/$id/ship/")
    db_char.ship_id = ship['ship_type_id']

    db_char.save()

    print "Updated location info for character %s" % db_char.name


@app.task(name="spawn_price_updates")
def spawn_price_updates(inline=False):
    def chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    id_chunks = chunks(
        list(
            Type.objects.filter(
                published=True,
                market_group__isnull=False
            ).values_list(
                'id',
                flat=True
            )
        ),
        500
    )

    for chunk in id_chunks:
        if inline:
            update_prices(chunk)
        else:
            update_prices.delay(chunk)
    print "Queued price updates"


@app.task(name="update_prices")
def update_prices(item_ids):
    r = requests.get(
        "https://market.fuzzwork.co.uk/aggregates/",
        params={
            "region": 10000002,
            "types": ",".join(map(str, item_ids))
        }
    ).json()

    with transaction.atomic():
        for key in r.keys():
            item = r[key]
            db_type = Type.objects.get(id=int(key))
            db_type.buy = item['buy']['percentile']
            db_type.sell = item['sell']['percentile']
            db_type.save()

    print "Price updates completed for %s:%s" % (
        item_ids[0],
        item_ids[-1]
    )


@app.task(name="spawn_kill_updates")
def spawn_kill_updates():
    chars = Character.objects.filter(owner__isnull=False)
    for char in chars.all():
        update_kills.delay(char.id)
    print "Spawned kill updates for %s characters" % chars.count()


@app.task(name="update_kills")
def update_kills(char_id):
    char = Character.objects.get(id=char_id)
    kills = requests.get("https://zkillboard.com/api/kills/characterID/%s/" % char_id).json()

    new = 0
    for kill in kills:
        if "character_id" in kill['victim']:
            db_kill, created = Kill.objects.get_or_create(
                id=kill['killmail_id'],
                defaults={
                    'victim': Character.get_or_create(
                            kill['victim']['character_id']
                        ),
                    'ship_id': kill['victim']['ship_type_id'],
                    'system_id': kill['solar_system_id'],
                    'price': kill['zkb']['totalValue'],
                    'date': parse_api_date(kill['killmail_time'])
                }
            )

            if created:
                new = new + 1
                for attacker in kill['attackers']:
                    if "character_id" in attacker:
                        db_kill.killers.add(
                            Character.get_or_create(attacker['character_id'])
                        )

    print "Added %s new kills for %s" % (
        new,
        char.name
    )
