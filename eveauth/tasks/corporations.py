from datetime import timedelta

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from avrseauth.celery import app

from eveauth.esi import ESI, parse_api_date
from eveauth.models.corporation import Corporation
from eveauth.models.structure import Service
from eveauth.models.structure import Structure

from alerts import embeds
from alerts.models import Webhook
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
    # Look for character with the right roles
    corp = Corporation.objects.get(id=corp_id)
    director = corp.characters.filter(
        roles__name="Director",
        token__isnull=False,
        token__extra_data__contains="esi-corporations.read_structures.v1"
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

        if len(structures) > 0:
            with transaction.atomic():
                for structure in structures:
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


        print "Updated all info for Corporation %s" % corp.name