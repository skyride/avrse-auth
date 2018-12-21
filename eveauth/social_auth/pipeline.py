from django.conf import settings

from alerts.models import Webhook
from alerts.embeds import character_added

from eveauth import tasks
from eveauth.models import Character


def update_user(backend, user, response, *args, **kwargs):
    if backend.name == "eveonline":
        tasks.update_groups(user.id)


# Do the custom associate for character_auth
def associate_user(backend, uid, response, user=None, social=None, *args, **kwargs):
    if social == None:
        social = backend.strategy.storage.user.create_social_auth(
            user, uid, backend.name
        )

        return {'social': social}


# Add the scopes to the extra_data
def scopes(backend, user, response, social=None, *args, **kwargs):
    # Add scopes to extra data
    social.extra_data['scopes'] = settings.SOCIAL_AUTH_CHARACTER_AUTH_SCOPE


# Do the set up for the character when they're added
def update_character(backend, user, response, social=None, *args, **kwargs):
    from eveauth.tasks import update_character

    # Create character
    character = Character.get_or_create(response['CharacterID'])

    # Attach details
    character.token = social
    character.owner = user
    character.save()

    # Call an update on the characters groups
    tasks.update_groups.delay(user.id)
    update_character(response['CharacterID'])
    character = Character.get_or_create(response['CharacterID'])

    # Generate event
    Webhook.send(
        "character_added",
        character_added(user, character)
    )