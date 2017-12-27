import math

from django import template
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.models import Group
from django.utils import timezone

from eveauth.tasks import get_server

register = template.Library()


@register.filter(name="has_group")
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.filter(name="time")
def pretty_time_delta(seconds):
    seconds = int(seconds)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days > 0:
        return '%dd %dh %dm %ds' % (days, hours, minutes, seconds)
    elif hours > 0:
        return '%dh %dm %ds' % (hours, minutes, seconds)
    elif minutes > 0:
        return '%dm %ds' % (minutes, seconds)
    else:
        return '%ds' % (seconds,)


@register.filter(name="channel")
def channel(id):
    if settings.MUMBLE_HOST == "":
        return "CHANNEL_NAME"

    # Try cache
    key = "murmur_channel_name:%s"
    name = cache.get(key % id)
    if name != None:
        return name

    # Populate cache
    murmur = get_server()
    for channel in murmur.getChannels():
        cache.set(key % channel.id, channel.name, 60)
        if channel.id == id:
            name = channel.name
    murmur.ice_getCommunicator().destroy()

    return name


@register.filter(name="level")
def level(id):
    return ["Non-member", "Blue", "Member"][id]


@register.filter(name="since")
def since(timestamp):
    delta = timezone.now() - timestamp
    return pretty_time_delta(delta.total_seconds())


@register.filter(name="until")
def until(timestamp):
    delta = timestamp - timezone.now()
    return pretty_time_delta(delta.total_seconds())


@register.filter(name="outstandingapps")
def outstandingapps(group):
    return group.apps.filter(accepted=None).count()
