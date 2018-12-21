from datetime import timedelta

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from avrseauth.celery import app
from avrseauth.settings import members

from eveauth.esi import ESI, parse_api_date
from eveauth.models.character import Character
from eveauth.models.corporation import Corporation
from eveauth.models.structure import Service, Structure

from alerts import embeds
from alerts.models import Webhook
from alerts.embeds import character_joined, character_left

from sde.models import Station
from timerboard.models import Timer


# Update data on all corporations with director tokens
@app.task(name="spawn_corporation_updates", expires=3600)
def spawn_corporation_updates():
    corps = Corporation.objects.filter(
        characters__token__isnull=False,
        characters__roles__name="Director"
    ).distinct()
    for corp in corps:
        update_corporation.delay(corp.id)


# Update all corp data from the first available director API
@app.task(name="update_corporation", expires=3600)
def update_corporation(corp_id):
    corp = Corporation.objects.get(id=corp_id)
    api = ESI()
    corp_details = api.get("/v4/corporations/%s/" % corp.id)
    if corp_details is not None:
        alliance_id = corp_details.get('alliance_id', None)

    # Structures
    director = corp.characters.filter(
        roles__name="Director",
        token__isnull=False,
        token__extra_data__contains="esi-corporations.read_structures.v1"
    ).first()

    if director != None:
        api = ESI(director.token)

        structures = api.get("/v2/corporations/%s/structures/" % corp.id)
        corp.structures.exclude(
            id__in=map(
                lambda x: x['structure_id'],
                structures
            )
        ).delete()

        if len(structures) > 0:
            with transaction.atomic():
                for structure in structures:
                    db_structure = Structure.objects.filter(id=structure['structure_id']).first()
                    if db_structure == None:
                        db_structure = Structure(id=structure['structure_id'])

                    previous_state = db_structure.state

                    # Try to update name
                    info = api.get("/v1/universe/structures/%s/" % structure['structure_id'])
                    if info is not None:
                        station = db_structure.station
                        station.name = info['name']
                        station.save()

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
                                stage={"armor_reinforce": "AR", "hull_reinforce": "ST", "anchoring": "AN", "unanchoring": "UN"}[structure['state']],
                                visible_to_level=2,
                                created_by=User.objects.first(),
                                generated=True
                            )
                            timer.save()

                            # Structure reinforce webhook
                            if db_structure.state in ["armor_reinforce", "hull_reinforce"]:
                                Webhook.send(
                                    "structure_reinforce",
                                    embeds.structure_state(timer, db_structure)
                                )
                            # Structure anchoring webhook
                            if db_structure.state in ["anchoring", "unanchoring"]:
                                Webhook.send(
                                    "structure_anchoring",
                                    embeds.structure_state(timer, db_structure)
                                )

                    # Ping about fuel if necessary
                    if db_structure.fuel_expires != None:
                        time_left = db_structure.fuel_expires - timezone.now()
                        if time_left <= timedelta(hours=72):
                            hours_left = int(time_left.total_seconds() / 60 / 60)
                            if hours_left % 12 == 0:
                                if db_structure.fuel_notifications:
                                    Webhook.send(
                                        "low_fuel_filtered",
                                        embeds.low_fuel(db_structure)
                                    )

                                Webhook.send(
                                    "low_fuel_all",
                                    embeds.low_fuel(db_structure)
                                )


        print "Updated structures for %s" % corp.name

    # Member Tracking
    director = corp.characters.filter(
        roles__name="Director",
        token__isnull=False,
        token__extra_data__contains="esi-corporations.read_corporation_membership.v1"
    ).first()

    if director != None:
        api = ESI(director.token)

        # Work on differences
        character_ids = api.get("/v3/corporations/%s/members/" % corp.id)
        if character_ids is not None:
            # Create diffs
            new_character_ids = set(character_ids)
            db_character_ids = set(Character.objects.filter(corp=corp).values_list('id', flat=True))
            joined_chars = new_character_ids - db_character_ids
            joined_chars = Character.objects.filter(id__in=joined_chars).all()
            left_chars = db_character_ids - new_character_ids
            left_chars = Character.objects.filter(id__in=left_chars).all()

            # Generate webhook events
            for joined_char in joined_chars:
                if joined_char.token is not None:
                    if joined_char.id in members['alliances'] or corp.id in members['corps'] or alliance_id in members['chars']:
                        Webhook.send("character_joined", character_joined(joined_char, corp))
            for left_char in left_chars:
                if left_char.id in members['alliances'] or corp.id in members['corps'] or alliance_id in members['chars']:
                    Webhook.send("character_left", character_left(left_char, corp))

            # Null the corp on chars that have left
            left_chars.update(corp=None, alliance=None)

        corp_members = api.get("/v1/corporations/%s/membertracking/" % corp.id)

        if corp_members is not None:
            with transaction.atomic():
                for member in corp_members:
                    char = Character.get_or_create(member['character_id'])
                    char.corp = corp
                    char.last_login = parse_api_date(member['logon_date'])
                    char.last_logoff = parse_api_date(member['logoff_date'])
                    char.ship_id = member['ship_type_id']
                    char.save()

        print "Updated %s members for %s" % (len(corp_members), corp.name)