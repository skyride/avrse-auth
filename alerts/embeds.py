

def structure_reinforce(timer, structure):
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