from __future__ import unicode_literals

import json
from datetime import timedelta
from hashlib import sha1

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.utils.crypto import get_random_string
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from django.db import IntegrityError

from eveauth.models import Templink, TemplinkUser, GroupApp
from eveauth.tasks import purge_templink_users, update_groups, update_discord
from eveauth.ipb import IPBUser


def home(request):
    if not request.user.is_authenticated():
        return render(request, "eveauth/home.html")
    else:
        return redirect(services)


@login_required
def services(request):
    context = {
        "discord": request.user.social_auth.filter(provider="discord").first(),
        "invite_key": settings.DISCORD_INVITE_KEY,
        "mumble_host": settings.MUMBLE_HOST,
        "mumble_port": settings.MUMBLE_PORT,
        "forum_address": settings.FORUM_ADDRESS,
        "mumble_access_level": settings.MUMBLE_ACCESS_LEVEL,
        "discord_access_level": settings.DISCORD_ACCESS_LEVEL
    }

    return render(request, "eveauth/services.html", context)


@login_required
def groups_index(request):
    my_groups = request.user.groups.exclude(
        Q(name__startswith="Alliance: ") | Q(name__startswith="Corp: ")
    ).order_by('name').all()
    my_groups_map = map(lambda x: x.id, my_groups)
    my_apps = request.user.group_apps.filter(accepted=None).all()
    my_apps_map = map(lambda x: x.group.id, my_apps)

    context = {
        "my_groups": my_groups,
        "open_groups": Group.objects.filter(
            details__is_open=True
        ).exclude(
            id__in=my_groups_map
        ).all(),
        "apply": Group.objects.filter(
            details__can_apply=True
        ).exclude(
            id__in=my_groups_map
        ).all(),
        "my_apps": my_apps_map
    }

    return render(request, "eveauth/groups_index.html", context)


@login_required
def groups_leave(request, group_id):
    group = Group.objects.get(id=group_id)
    request.user.groups.remove(group)
    messages.success(request, "Left group %s" % group.name)

    update_discord.delay(request.user.id)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def groups_join(request, group_id):
    group = Group.objects.get(id=group_id)
    if group.details.is_open == True:
        request.user.groups.add(group)
        messages.success(request, "Joined group %s" % group.name)

        update_discord.delay(request.user.id)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def groups_apply(request, group_id):
    group = Group.objects.get(id=group_id)
    if group.details.can_apply == True:
        app = GroupApp(
            user=request.user,
            group=group
        )
        app.save()

        messages.success(request, "Applied to %s" % group.name)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def toggle_theme(request):
    if not "theme" in request.session:
        request.session['theme'] = "darkly"
    elif request.session['theme'] == "darkly":
        request.session['theme'] = "flatly"
    else:
        request.session['theme'] = "darkly"

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def update_mumble_password(request):
    profile = request.user.profile

    hasher = PBKDF2PasswordHasher()
    password = request.POST.get("mumble_password")
    password = hasher.encode(password, get_random_string(12))
    profile.mumble_password = password

    profile.save()
    messages.success(request, 'Updated mumble password')
    return redirect(services)


@login_required
def update_forum_password(request):
    profile = request.user.profile

    password = request.POST.get("forum_password")
    profile.forum_username = profile.character.name
    profile.save()

    ipb = IPBUser(request.user)
    ipb.update_password(password)

    messages.success(request, 'Updated forum password')
    return redirect(services)
