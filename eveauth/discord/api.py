from sets import Set

from disco.api.client import APIClient
from disco.api.http import Routes
from django.conf import settings


def is_active():
    return settings.DISCORD_BOT_TOKEN != ""


class DiscordAPI:

    def __init__(self):
        self.api = APIClient(settings.DISCORD_BOT_TOKEN)
        self.guild = self.api.http(Routes.USERS_ME_GUILDS_LIST).json()[0]


    def is_user_in_guild(self, user_id):
        members = self.api.guilds_members_list(self.guild['id']).keys()
        return int(user_id) in members


    def kick_member(self, user_id):
        try:
            reason = "User no longer had the correct access level for discord"
            self.api.guilds_members_kick(self.guild['id'], user_id, reason)
            return True
        except:
            return False


    def set_name(self, user_id, name):
        try:
            self.api.guilds_members_modify(self.guild['id'], user_id, nick=name)
            return True
        except:
            return False


    # Roles is a list of role name strings
    def update_roles(self, user_id, roles):
        # Find roles we need to create
        guild_roles = self.api.guilds_roles_list(self.guild['id'])
        guild_roles_map = map(lambda x: x.name, guild_roles)
        for role_name in Set(roles).difference(guild_roles_map):
            role = self.api.guilds_roles_create(self.guild['id'])
            self.api.guilds_roles_modify(self.guild['id'], role.id, name=role_name)
            guild_roles.append(role)

        # Build snowflake list
        snowflakes = []
        for role in roles:
            snowflakes.append(filter(lambda x: x.name == role, guild_roles)[0].id)

        self.api.guilds_members_modify(self.guild['id'], user_id, roles=snowflakes)
