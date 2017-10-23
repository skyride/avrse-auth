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


class AuthPlugin(Plugin):
    @Plugin.listen('MessageCreate')
    def command_evetime(self, event):
        if event.content == "!evetime":
            event.reply(datetime.utcnow().strftime("EVETime: %H:%M:%S"))


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
