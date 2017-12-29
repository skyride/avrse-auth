from eveauth.models import Character


class BotCommands:
    def __init__(self, tokens, user, event):
        self.tokens = tokens
        self.user = user
        self.event = event


    def monowrap(self, text):
        return "```%s```" % text

    def get_personal_chars(self):
        search = " ".join(self.tokens[1:])
        return self.user.characters.filter(name__istartswith=search)

    def get_all_chars(self):
        search = " ".join(self.tokens[1:])
        return Character.objects.filter(
            owner__isnull=False,
            name__istartswith=search
        )


    def fatigue(self, admin=False):
        if admin:
            chars = self.get_all_chars()
        else:
            chars = self.get_personal_chars()

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
                "**%s**: %s" % (
                    char.name,
                    char.fatigue_text()
                )
            )
