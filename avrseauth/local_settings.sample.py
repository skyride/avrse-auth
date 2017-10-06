import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# These are the settings you should update
# SECURITY WARNING: keep the secret key used in production secret! Generate a random string
SECRET_KEY = 'asdasd'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

CELERY_APP_NAME = "avrseauth"
BROKER_URL = "redis://127.0.0.1:6379/1"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/1"

SOCIAL_AUTH_EVEONLINE_KEY = ""
SOCIAL_AUTH_EVEONLINE_SECRET = ""

ESI_URL = "https://esi.tech.ccp.is/latest"
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

members = {
    "alliances": [
    ],
    "corps": [
    ]
}

blues = {
    "alliances": [
    ],
    "corps": [
    ]
}
