from django.conf import settings

from eveauth import tasks


def update_user(backend, user, response, *args, **kwargs):
    if backend.name == "eveonline":
        tasks.update_groups(user.id)


def associate_user(backend, uid, response, user=None, social=None, *args, **kwargs):
    if social == None:
        social = backend.strategy.storage.user.create_social_auth(
            user, uid, backend.name
        )

        return {'social': social}


def scopes(backend, user, response, social=None, *args, **kwargs):
    # Add scopes to extra data
    social.extra_data['scopes'] = settings.SOCIAL_AUTH_CHARACTER_AUTH_SCOPE


def update_character(backend, user, response, social=None, *args, **kwargs):
    if backend.name == "character_auth":
        tasks.update_character(response['CharacterID'])
