import os, sys
import django
sys.path.append("../")
os.environ['DJANGO_SETTINGS_MODULE'] = 'avrseauth.settings'
django.setup()

from datetime import datetime

from django.db.models import Q
from django.conf import settings

from disco.bot import Plugin
from social_django.models import UserSocialAuth

from eveauth.discord.commands import BotCommands
from sde.models import System


class AuthPlugin(Plugin):
    # Public commands
    @Plugin.listen('MessageCreate')
    def public_commands(self, event):
        tokens = event.content.split()

        if tokens[0] == "!evetime":
            event.reply(datetime.utcnow().strftime("EVETime: %H:%M:%S"))
        elif tokens[0] == "!range":
            system = System.objects.filter(
                name__istartswith=" ".join(tokens[1:])
            )
            if system.count() > 1:
                event.reply(
                    "```Multiple Systems Found:\n%s```" % (
                        ", ".join(system.all().values_list('name', flat=True))
                    )
                )
            elif system.count() == 1:
                system = system.first()
                event.reply(
                    "\n".join(
                        [
                            "http://evemaps.dotlan.net/range/Redeemer,5/%s" % system.name.replace(" ", "_"),
                            "http://evemaps.dotlan.net/range/Archon,5/%s" % system.name.replace(" ", "_"),
                            "http://evemaps.dotlan.net/range/Aeon,5/%s" % system.name.replace(" ", "_")
                        ]
                    )
                )


    # FC Tools
    @Plugin.listen('MessageCreate')
    def fc_commands(self, event):
        # Tokenise commands
        tokens = event.content.split()
        if tokens[0].startswith("!"):
            user = self._get_social(event.member.id).user
            commands = BotCommands(tokens, user, event)

            admin = user.groups.filter(name="fc").exists()
            # Admin only commands
            if admin:
                if tokens[0].lower() == "!fatigue":
                    commands.fatigue(admin=True)
                if tokens[0].lower() == "!alts":
                    commands.alts()


            # public commands with limitations
            else:
                if tokens[0].lower() == "!fatigue":
                    commands.fatigue(admin=False)


    # Handle guild member joins
    @Plugin.listen('GuildMemberAdd')
    def guild_member_join(self, event):
        # Kick the user if they aren't authed
        social = self._get_social(event.member.id)
        if not social:
            if event.member.id not in settings.DISCORD_ALLOWED_BOTS:
                return
            else:
                event.member.kick()

        # Set their nickname to their EVE Character
        event.member.set_nickname(social.user.profile.character.name)

        # Set corp role
        event.member.add_role(self._get_role(event.guild, social.user.profile.corporation.ticker))

        # Set regular group roles
        groups = social.user.groups.exclude(
            Q(name__startswith="Corp: ") | Q(name__startswith="Alliance: ")
        ).all()
        for group in groups:
            event.member.add_role(self._get_role(event.guild, group.name))

        # Set Access Level Group
        access_level = ["Non-member", "Blue", "Member"][social.user.profile.level]
        event.member.add_role(self._get_role(event.guild, access_level))


    # Try to get the social object from a discord ID. Return None if not found
    def _get_social(self, uid):
        return UserSocialAuth.objects.filter(uid=uid).first()


    # Get a role object from a string
    def _get_role(self, guild, name):
        # Check if the role already exists
        for role in guild.roles.values():
            if role.name == name:
                return role

        # It doesn't so lets make it
        role = guild.create_role()
        self.client.api.guilds_roles_modify(guild.id, role.id, name=name)
        return role
