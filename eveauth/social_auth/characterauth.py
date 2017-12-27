from social_core.backends.eveonline import EVEOnlineOAuth2


class EVECharacterAuth(EVEOnlineOAuth2):
    name = 'character_auth'
