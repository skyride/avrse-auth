import math

from django import template
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.models import Group
from django.db.models import Sum
from django.utils import timezone
from django.utils.safestring import mark_safe

from eveauth.tasks import get_server

register = template.Library()


@register.filter(name="has_group")
def has_group(user, group_names):
    group_names = group_names.split(",")
    return user.groups.filter(name__in=group_names).exists()


@register.filter(name="beautify")
def beautify(string):
    return string.replace("_", " ")

@register.filter(name="servicestate")
def servicestate(state):
    if state:
        return "<span class='text-success'>Online</span>"
    else:
        return "<span class='text-danger'>Offline</span>"


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
    channels = murmur.getChannels()
    for channel in channels:
        channel = channels[channel]
        cache.set(key % channel.id, channel.name, 60)
        if channel.id == id:
            name = channel.name
    murmur.ice_getCommunicator().destroy()

    return name


@register.filter(name="level")
def level(id):
    if id in [0, 1, 2]:
        return ["Non-member", "Blue", "Member"][id]
    else:
        return "ERROR"


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


@register.filter(name="roman")
def roman(num):
    return ["", "I", "II", "III", "IV", "V"][num]


@register.filter(name="levelicon")
def levelicon(skill, level):
    if level > skill.active_skill_level:
        if level > skill.trained_skill_level:
            return mark_safe('<i class="far fa-square"></i>')
        else:
            return mark_safe('<i class="fas fa-square text-warning"></i>')
    return mark_safe('<i class="fas fa-square"></i>')


@register.filter(name="typesum")
def typesum(types):
    return types.aggregate(
        total=Sum('type__sell')
    )['total']


@register.filter(name="fatiguetime")
def fatiguetime(delta):
    out = "%.2i:%.2i:%.2i" % (
        (delta.seconds / 60 / 60) % 24,
        (delta.seconds / 60) % 60,
        delta.seconds % 60
    )

    if delta.days > 0:
        out = "%sD %s" % (str(delta.days), out)

    return out
