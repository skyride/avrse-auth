from flarum.api import FlarumAPI
from flarum.models import FlarumGroup, FlarumUser


def create_group(name_singular, name_plural, type="group"):
    api = FlarumAPI()
    id = api.create_group(name_singular, name_plural)
    group = FlarumGroup.objects.create(
        id=id,
        name_singular=name_singular,
        name_plural=name_plural,
        type=type
    )
    return group


def get_or_create_group(name_singular, name_plural, *args, **kwargs):
    try:
        return FlarumGroup.objects.get(name_singular=name_singular)
    except FlarumGroup.DoesNotExist:
        return create_group(name_singular, name_plural, *args, **kwargs)


def create_user(user, password):
    api = FlarumAPI()
    id = api.create_user(user.username, "%s@auth.com" % user.username, password)
    user = FlarumUser.objects.create(
        id=id,
        username=user.username,
        user=user,
        email="%s@auth.com" % user.username
    )
    return user