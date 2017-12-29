from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings
from django.db import transaction
from django.db.models import Q

from avrseauth.settings import members, blues
from avrseauth.celery import app

from sde.models import System, Station

from eveauth import ipb
from eveauth.models.character import Character
from eveauth.models.corporation import Corporation
from eveauth.models.alliance import Alliance
from eveauth.models.templink import Templink
from eveauth.models.skill import Skill
from eveauth.models.asset import Asset
from eveauth.esi import ESI, parse_api_date
from eveauth.discord.api import DiscordAPI, is_bot_active


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
    corp_id = user.profile.corporation_id
    alliance_id = user.profile.alliance_id

    if corp_id in members['corps'] or alliance_id in members['alliances']:
        user.profile.level = 2
    elif corp_id in blues['corps'] or alliance_id in blues['alliances']:
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
        assets = api.get("/v3/characters/$id/assets/")
        with transaction.atomic():
            Asset.objects.filter(character=db_char).delete()
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
