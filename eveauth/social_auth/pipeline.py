from eveauth.tasks import update_groups


def update_user(backend, user, response, *args, **kwargs):
    if backend.name == "eveonline":
        update_groups(user.id)
