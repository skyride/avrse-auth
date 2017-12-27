from eveauth.tasks import update_groups


def update_user(backend, user, response, *args, **kwargs):
    if backend.name == "eveonline":
        update_groups(user.id)


def update_character(backend, user, response, *args, **kwargs):
    if backend.name == "character_auth":
        pass
