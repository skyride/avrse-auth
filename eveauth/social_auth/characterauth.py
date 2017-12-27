from social_core.backends.eveonline import EVEOnlineOAuth2


# Secondary SSO connection for connecting characters
class EVECharacterAuth(EVEOnlineOAuth2):
    name = 'character_auth'
