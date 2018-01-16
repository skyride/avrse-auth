import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# These are the settings you should update
# SECURITY WARNING: keep the secret key used in production secret! Generate a random string
SECRET_KEY = 'asdasd'
AUTH_NAME = "AVRSE Auth"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

CELERY_APP_NAME = "avrseauth"
BROKER_URL = "redis://127.0.0.1:6379/1"

# For login
SOCIAL_AUTH_EVEONLINE_KEY = ""
SOCIAL_AUTH_EVEONLINE_SECRET = ""

# For characters
SOCIAL_AUTH_CHARACTER_AUTH_KEY = ""
SOCIAL_AUTH_CHARACTER_AUTH_SECRET = ""

# Leave blank if you don't want to use discord
SOCIAL_AUTH_DISCORD_KEY = ""
SOCIAL_AUTH_DISCORD_SECRET = ""
DISCORD_BOT_TOKEN = ""
DISCORD_INVITE_KEY = ""
DISCORD_ACCESS_LEVEL = 2
DISCORD_ALLOWED_BOTS = []

ESI_URL = "https://esi.tech.ccp.is"
ESI_DATASOURCE = "tranquility"
ESI_RETRIES = 15

MUMBLE_HOST = ""
MUMBLE_PORT = 64738
MUMBLE_ACCESS_LEVEL = 1     # 0 = anyone, 1 = blues and members, 2 = members
MUMBLE_AUTO_AFK = True
MUMBLE_AUTO_AFK_DELAY = 20
MUMBLE_AUTO_AFK_CHANNEL = 0

FORUM_ADDRESS = "https://forums.example.com/"
FORUM_API_KEY = ""
FORUM_ACCESS_GROUPS = [
    11,     # Non-Members
    10,     # Blues
    3,      # Members
]

members = {
    "alliances": [
    ],
    "corps": [
    ],
    "chars": [
    ]
}

blues = {
    "alliances": [
    ],
    "corps": [
    ],
    "chars": [
    ]
}
