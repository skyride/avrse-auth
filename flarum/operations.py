from flarum.api import FlarumAPI
from flarum.models import FlarumGroup


def create_group(name_singular, name_plural, type="group"):
    api = FlarumAPI()
    id = api.create_group(name_singular, name_plural)
    group = FlarumGroup.objects.create(
        id=id,
        name_singular=name_singular,
        name_plural=name_plural,
        type=type
    )
    print "Created flarum group %s" % str(group)
    return group


def get_or_create_group(name_singular, name_plural, *args, **kwargs):
    try:
        return FlarumGroup.objects.get(name_singular=name_singular)
    except FlarumGroup.DoesNotExist:
        return create_group(name_singular, name_plural, *args, **kwargs)