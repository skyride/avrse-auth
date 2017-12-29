

class BotCommands:
    def __init__(self, tokens, user, event):
        self.tokens = tokens
        self.user = user
        self.event = event


    def monowrap(self, text):
        return "```%s```" % text


    def fatigue(self):
        # Find chars
        search = self.tokens[1]
        chars = self.user.characters.filter(name__istartswith=search)

        if chars.count() == 0:
            self.event.reply("No characters found")
        elif chars.count() > 1:
            self.event.reply(
                self.monowrap(
                    "Multiple chars found: %s" % (
                        ",".join(
                            map(lambda x: x.name, chars.all())
                        )
                    )
                )
            )
        else:
            char = chars.first()
            self.event.reply(
                self.monowrap(
                    "Owner: %s\nCharacter: %s\nFatigue: %s\nSystem: %s\nRegion: %s\nShip: %s" %(
                        self.user.profile.character.name,
                        char.name,
                        char.fatigue_text(),
                        char.system.name,
                        char.system.region.name,
                        char.ship.name
                    )
                )
            )
