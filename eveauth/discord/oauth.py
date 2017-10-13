from social_core.backends.oauth import BaseOAuth2

import requests


# Discord Social Core Authentication
class DiscordOAuth2(BaseOAuth2):
    """Discord OAuth authentication backend"""
    name = 'discord'
    BASE_URL = "https://discordapp.com/api"
    AUTHORIZATION_URL = "%s/oauth2/authorize" % BASE_URL
    ACCESS_TOKEN_URL = "%s/oauth2/token" % BASE_URL
    ACCESS_TOKEN_METHOD = 'POST'
    REDIRECT_STATE = False
    SCOPE_SEPARATOR = ' '
    EXTRA_DATA = [
        ('username', 'username'),
        ('discriminator', 'discriminator'),
        ('avatar', 'avatar'),
        ('mfa_enabled', 'mfa_enabled')
    ]

    def get_user_details(self, response):
        """Return user details"""
        return {}

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        headers = {
            "Authorization": "Bearer %s" % access_token
        }
        return requests.get("%s/users/@me" % self.BASE_URL, headers=headers).json()
