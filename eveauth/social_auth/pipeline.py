from eveauth  import tasks


def update_user(backend, user, response, *args, **kwargs):
    if backend.name == "eveonline":
        tasks.update_groups(user.id)


def update_character(backend, user, response, *args, **kwargs):
    if backend.name == "character_auth":
        tasks.update_character(response['CharacterID'])
