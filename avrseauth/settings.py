"""
Django settings for avrseauth project.

Generated by 'django-admin startproject' using Django 1.11.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
_PATH = os.path.realpath(os.path.join(os.path.dirname(__file__), '../..'))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'social_django',
    'mathfilters',

    'eveauth',
    'timerboard',
    'esi',
    'sde'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'social_core.backends.eveonline.EVEOnlineOAuth2',
    'eveauth.social_auth.characterauth.EVECharacterAuth',
    'eveauth.discord.oauth.DiscordOAuth2',
)

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
    'social_core.pipeline.social_auth.associate_by_email',
    'eveauth.social_auth.pipeline.update_user',
)

SOCIAL_AUTH_CHARACTER_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.associate_user',
    'eveauth.social_auth.pipeline.scopes',
    'social_core.pipeline.social_auth.load_extra_data',
    'eveauth.social_auth.pipeline.update_character',
)

ROOT_URLCONF = 'avrseauth.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                'eveauth.middleware.global_vars',
            ],
        },
    },
]

WSGI_APPLICATION = 'avrseauth.wsgi.application'



# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/services/'
SOCIAL_AUTH_CLEAN_USERNAMES = True

SOCIAL_AUTH_CHARACTER_AUTH_LOGIN_REDIRECT_URL = '/characters/'

SOCIAL_AUTH_EVEONLINE_SCOPE = [
    "publicData"
]
SOCIAL_AUTH_CHARACTER_AUTH_SCOPE = [
    "esi-assets.read_assets.v1",                    # SEE UR STUFF
    "esi-characters.read_corporation_roles.v1",     # SEE UR ROLES
    "esi-characters.read_fatigue.v1",               # SEE UR SPACE AIDS
    "esi-clones.read_clones.v1",                    # SEE UR JUMP CLONES
    "esi-clones.read_implants.v1",                  # SEE UR IMPLANTS
    "esi-location.read_location.v1",                # SEE WHERE UR AT
    "esi-location.read_online.v1",
    "esi-location.read_ship_type.v1",
    "esi-search.search_structures.v1",              # SEE SHITADELS UR STUFF IS IN
    "esi-universe.read_structures.v1",
    "esi-skills.read_skills.v1",                    # SEE UR SKILLS
    "esi-skills.read_skillqueue.v1",
    "esi-wallet.read_character_wallet.v1"           # SEE UR SPACE GOLD
]
SOCIAL_AUTH_DISCORD_SCOPE = [
    "identify"
]


# Celery
CELERY_IGNORE_RESULT = False
CELERY_TASK_RESULT_EXPIRES = 1200

CELERY_DISABLE_RATE_LIMITS = True
CELERYD_TASK_SOFT_TIME_LIMIT = 300
CELERYD_PREFETCH_MULTIPLIER = 1
CELERY_STORE_ERRORS_EVEN_IF_IGNORED = True


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(_PATH, 'static')

# How many hours between rechecking user groups via API
USER_UPDATE_DELAY = 1


from datetime import timedelta
CELERYBEAT_SCHEDULE = {
    # Update user groups once an hour
    'spawn_groupupdates': {
        'task': 'spawn_groupupdates',
        'schedule': timedelta(hours=USER_UPDATE_DELAY)
    },
    'spawn_price_updates': {
        'task': 'spawn_price_updates',
        'schedule': timedelta(hours=24)
    },
    'spawn_kill_updates': {
        'task': 'spawn_kill_updates',
        'schedule': timedelta(hours=12)
    },
    'spawn_character_location_updates': {
        'task': 'spawn_character_location_updates',
        'schedule': timedelta(minutes=5)
    },
    'purge_expired_templinks': {
        'task': 'purge_expired_templinks',
        'schedule': timedelta(seconds=5)
    },
    'mumble_afk_check': {
        'task': 'mumble_afk_check',
        'schedule': timedelta(seconds=5)
    }
}

LOGIN_URL = "/"

from local_settings import *

# SDE Database
DATABASES['sde'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': os.path.join(BASE_DIR, 'sqlite-latest.sqlite'),
}
#DATABASES['default']['OPTIONS'] = {'charset': 'utf8mb4'}
