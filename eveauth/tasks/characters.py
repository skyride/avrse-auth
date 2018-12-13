import ujson as json
import requests
import time

from datetime import timedelta

from django.core.cache import cache
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from alerts import embeds
from alerts.models import Webhook

from avrseauth.celery import app

from eveauth.esi import ESI, parse_api_date
from eveauth.models.asset import Asset
from eveauth.models.alliance import Alliance
from eveauth.models.character import Character
from eveauth.models.clone import Clone, CloneImplant
from eveauth.models.corporation import Corporation
from eveauth.models.implant import Implant
from eveauth.models.kill import Kill
from eveauth.models.role import Role
from eveauth.models.skill import Skill, SkillTraining
from eveauth.models.notification import Notification

from sde.models import Station


# Update location for characters with tokens
@app.task(name="spawn_character_location_updates", expires=300)
def spawn_character_location_updates():
    chars = Character.objects.filter(
        token__isnull=False
    ).all()
    for char in chars:
        update_character_location.delay(char.id)

    print "Spawned character location update tasks for %s chars" % chars.count()


@app.task(name="spawn_character_notification_updates", expires=300)
def spawn_character_notification_updates():
    chars = Character.objects.filter(
        token__isnull=False
    ).all()

    count = 0
    for char in chars:
        if "esi-characters.read_notifications.v1" in char.token.extra_data['scopes']:
            update_character_notifications.delay(char.id)
            count = count + 1

    print "Spawned notification updates for %s characters" % count


@app.task(name="update_character", expires=3600)
def update_character(character_id):
    # Start the timer
    start_time = time.time()

    db_char = Character.objects.get(id=character_id)

    with transaction.atomic():
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

        with transaction.atomic():
            # Check refresh token to see if it's still valid
            if api._refresh_access_token() == False:
                # Check if we've had 24 within the last 72hrs failures. This runs hourly so that means EVE would need to be dead for a full day.
                cache_key = "fail_history_character_%s" % db_char.id
                fail_history = cache.get(cache_key, [])
                if len(fail_history) > 24:
                    token = db_char.token

                    user = db_char.owner

                    db_char.owner = None
                    db_char.token = None
                    db_char.save()

                    token.delete()

                    Webhook.send(
                        "character_expired",
                        embeds.character_expired(
                            user,
                            db_char
                        )
                    )

                    fail_history = []
                else:
                    fail_history.append(timezone.now())

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
            Skill.objects.filter(character=db_char).delete()
            db_skills = []
            for skill in skills['skills']:
                db_skill = Skill(
                    character=db_char,
                    type_id=skill['skill_id'],
                    trained_skill_level=skill['trained_skill_level'],
                    active_skill_level=skill['active_skill_level'],
                    skillpoints_in_skill=skill['skillpoints_in_skill']
                )
                db_skills.append(db_skill)
            Skill.objects.bulk_create(db_skills)

            # Skill Queue
            skills_training = api.get("/v2/characters/$id/skillqueue/")
            SkillTraining.objects.filter(character=db_char).delete()
            db_skills_training = []
            for skill_training in skills_training:
                db_skill_training = SkillTraining(
                    character=db_char,
                    type_id=skill_training['skill_id'],
                    start_sp=skill_training['training_start_sp'],
                    end_sp=skill_training['level_end_sp'],
                    training_to_level=skill_training['finished_level'],
                    position=skill_training['queue_position']
                )
                if "start_date" in skill_training:
                    db_skill_training.starts = parse_api_date(skill_training['start_date'])
                    db_skill_training.ends = parse_api_date(skill_training['finish_date'])
                db_skills_training.append(db_skill_training)
            SkillTraining.objects.bulk_create(db_skills_training)

            # Assets
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

        print "Updated all info for character %s in %s seconds" % (db_char.name, time.time() - start_time)



@app.task(name="update_character_location", expires=300)
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


@app.task(name="update_character_notifications", expires=300)
def update_character_notifications(character_id):
    # Get the db objects we need
    db_char = Character.objects.prefetch_related('token').get(id=character_id)
    api = ESI(db_char.token)

    # Check token has the scope
    if "esi-characters.read_notifications.v1" in db_char.token.extra_data['scopes']:
        notifications = api.get("/v2/characters/$id/notifications/")

        # Add notifications that don't exist
        existing = set(
            Notification.objects.filter(
                id__in=map(lambda x: x['notification_id'], notifications)
            ).values_list(
                'id',
                flat=True
            )
        )

        for notification in notifications:
            with transaction.atomic():
                if notification['notification_id'] not in existing:
                    db_notification = Notification(
                        id=notification['notification_id'],
                        text=notification['text'],
                        sender_id=notification['sender_id'],
                        sender_type=notification['sender_type'],
                        date=parse_api_date(notification['timestamp']),
                        type=notification['type']
                    )
                    db_notification.save()
                    
                    # StructureUnderAttack webhook
                    if db_notification.type == "StructureUnderAttack":
                        # Check its within the last 30 mins
                        if db_notification.date > timezone.now() - timedelta(minutes=30):
                            Webhook.send(
                                "structure_attacked",
                                embeds.structure_attacked(db_notification, api)
                            )

        # Add character to notifications it doesn't yet belong to
        #existing = set(
        #    db_char.notifications.filter(
        #        id__in=map(lambda x: x['notification_id'], notifications)
        #    ).values_list(
        #        'id',
        #        flat=True
        #    )
        #)
        #new = set(map(lambda x: x['notification_id'], notifications)) - existing

        print "Updated notifications for character %s" % db_char.name


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

    with transaction.atomic():
        api = ESI()
        new = 0
        for kill in kills:
            details = api.get("/v1/killmails/%s/%s/" % (kill['killmail_id'], kill['zkb']['hash']))
            if "character_id" in details['victim']:
                db_kill, created = Kill.objects.get_or_create(
                    id=kill['killmail_id'],
                    defaults={
                        'victim': Character.get_or_create(
                                details['victim']['character_id']
                            ),
                        'ship_id': details['victim']['ship_type_id'],
                        'system_id': details['solar_system_id'],
                        'price': kill['zkb']['totalValue'],
                        'date': parse_api_date(details['killmail_time'])
                    }
                )

                if created:
                    new = new + 1
                    for attacker in details['attackers']:
                        if "character_id" in attacker:
                            db_kill.killers.add(
                                Character.get_or_create(attacker['character_id'])
                            )

    print "Added %s new kills for %s" % (
        new,
        char.name
    )
