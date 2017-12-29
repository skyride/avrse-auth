from django.conf import settings
from django.db.models import Q

from avrseauth.settings import members, blues
from eveauth.models import Character


class BotCommands:
    def __init__(self, tokens, user, event):
        self.tokens = tokens
        self.user = user
        self.event = event


    def monowrap(self, text):
        return "```%s```" % text

    def get_personal_chars(self):
        self.search = " ".join(self.tokens[1:])
        return self.user.characters.filter(name__istartswith=self.search)

    def get_all_chars(self):
        self.search = " ".join(self.tokens[1:])
        return Character.objects.filter(
            owner__isnull=False,
            name__istartswith=self.search
        )


    def fatigue(self, admin=False):
        if admin:
            chars = self.get_all_chars()
        else:
            chars = self.get_personal_chars()

        if self.search == "":
            self.event.reply(
                self.monowrap(
                    "!fatigue <partial character name>"
                )
            )

        elif chars.count() == 0:
            self.event.reply("No Characters Found")

        elif chars.count() > 1:
            self.event.reply(
                self.monowrap(
                    "Multiple Chars Found:\n%s" % (
                        ", ".join(
                            map(lambda x: x.name,
                                chars.filter(
                                    Q(corp__id__in=members['corps'])
                                    | Q(alliance__id__in=members['alliances'])
                                    | Q(corp__id__in=blues['corps'])
                                    | Q(alliance__id__in=blues['alliances'])
                                ).all()
                            )
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
