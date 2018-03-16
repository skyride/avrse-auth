from eveauth.esi import ESI
from eveauth.models.character import Character

from sde.models import System, Type, Station


def structure_state(timer, structure):
    return {
        "username": "Structure Bot",
        "embeds": [
            {
                "type": "rich",
                "title": "%s (%s) %s" % (
                    timer.system.name,
                    timer.system.region.name,
                    {
                        "AN": "started Anchoring",
                        "AR": "Reinforced into Armor",
                        "ST": "Reinforced into Structure",
                        "UN": "started Unanchoring"
                    }[timer.stage]
                ),
                "description": "%s - %s (%s)" % (
                    timer.system.name,
                    timer.name,
                    timer.structure.name
                ),
                "thumbnail": {
                    "url": "https://imageserver.eveonline.com/Render/%s_128.png" % structure.type_id
                },
                "color": {
                    "AN": 0x0000ff,
                    "AR": 0xffff00,
                    "ST": 0xff0000,
                    "UN": 0x0000ff
                }[timer.stage],
                "fields": [
                    {
                        "name": "Timer",
                        "value": timer.date.strftime("%Y/%m/%d %H:%M"),
                        "inline": True,
                    },
                    {
                        "name": "Owner",
                        "value": "%s [%s]" % (
                            structure.corporation.name,
                            structure.corporation.ticker
                        ),
                        "inline": True,
                    }
                ]
            }
        ]
    }


def low_fuel(structure):
    return {
        "username": "Structure Bot",
        "embeds": [
            {
                "type": "rich",
                "title": "%s is low on fuel" % structure.type.name,
                "description": "%s (%s)" % (
                    structure.station.name,
                    structure.type.name
                ),
                "thumbnail": {
                    "url": "https://imageserver.eveonline.com/Render/%s_128.png" % structure.type_id
                },
                "color": 0x00ffff,
                "fields": [
                    {
                        "name": "Fuel Expires",
                        "value": structure.fuel_expires.strftime("%Y/%m/%d %H:%M"),
                        "inline": True,
                    },
                    {
                        "name": "Owner",
                        "value": "%s [%s]" % (
                            structure.corporation.name,
                            structure.corporation.ticker
                        ),
                        "inline": True,
                    }
                ]
            }
        ]
    }


def structure_attacked(notification, api=ESI()):
    data = notification.data
    system = System.objects.get(id=data['solarsystemID'])
    structure_type = Type.objects.get(id=data['structureShowInfoData'][1])
    structure = Station.get_or_create(data['structureID'], api)
    attacker = Character.get_or_create(data['charID'])

    out = {
        "username": "Structure Bot",
        "embeds": [
            {
                "type": "rich",
                "title": "%s in %s is under attack" % (
                    structure_type.name,
                    system.name,
                ),
                "description": "%s (%s)" % (
                    structure.name,
                    system.region.name
                ),
                "url": "https://zkillboard.com/character/%s/" % attacker.id,
                "thumbnail": {
                    "url": "https://imageserver.eveonline.com/Render/%s_128.png" % structure_type.id
                },
                "color": 0xff0000,
                "fields": [
                    {
                        "name": "Owner",
                        "value": structure.corp_structure.corporation.name,
                        "inline": True,
                    },
                    {
                        "name": "Attacker",
                        "value": attacker.name,
                        "inline": True,
                    },
                    {
                        "name": "Attacker Corp",
                        "value": data['corpName'],
                        "inline": True,
                    }
                ]
            }
        ]
    }

    if "allianceName" in data:
        out['embeds'][0]['fields'].append(
            {
                "name": "Attacker Alliance",
                "value": data['allianceName'],
                "inline": True,
            }
        )

    return out