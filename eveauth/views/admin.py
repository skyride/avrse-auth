from __future__ import unicode_literals

import json
from datetime import timedelta

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator
from django.utils.crypto import get_random_string
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from django.db import IntegrityError

from eveauth.models import GroupApp
from eveauth.tasks import get_server, update_groups, spawn_groupupdates, update_discord



@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def registeredusers_index(request, page=1):
    users = User.objects.prefetch_related(
        "profile",
        "profile__character",
        "profile__corporation",
        "profile__alliance"
    ).order_by(
        "-last_login"
    ).all()
    paginator = Paginator(users, 25)

    context = {
        "users": paginator.page(page)
    }

    return render(request, "eveauth/registeredusers_index.html", context)



@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def user_updategroups(request, id):
    update_groups.delay(id)
    user = User.objects.get(id=id)
    messages.success(request, "Triggered group update for %s" % user.profile.character.name)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))



@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def user_updategroups_all(request):
    users = spawn_groupupdates()
    messages.success(request, "Triggered updates for %s users" % users)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))



@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def view_user(request, id):
    user = User.objects.get(id=id)

    context = {
        "user": user,
        "forum_address": settings.FORUM_ADDRESS
    }

    return render(request, "eveauth/user_view.html", context)



@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def groupadmin_index(request):
    groups = Group.objects.exclude(
        Q(name__startswith="Corp: ") | Q(name__startswith="Alliance: ")
    ).order_by(
        'name'
    ).all()

    context = {
        "groups": groups
    }

    return render(request, "eveauth/groupadmin_index.html", context)


@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def groupadmin_create(request):
    group = Group(name="New Group")
    group.save()

    return redirect(groupadmin_edit, group.id)


@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def groupadmin_edit(request, id):
    group = Group.objects.get(id=id)

    # Check if we need to update the group
    if request.POST.get("name", None) != None:
        group.name = request.POST.get("name")
        group.details.is_open = bool(request.POST.get("is_open", False))
        group.details.can_apply = bool(request.POST.get("can_apply", False))
        group.details.mumble = bool(request.POST.get("mumble", False))
        group.details.forum = bool(request.POST.get("forum", False))
        group.details.discord = bool(request.POST.get("discord", False))
        group.save()
        group.details.save()

    context = {
        "group": group,
        "apps": group.apps.filter(accepted=None).order_by('created').all()
    }

    return render(request, "eveauth/groupadmin_edit.html", context)


@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def groupadmin_app_complete(request, app_id, yesno):
    app = GroupApp.objects.get(id=app_id)
    if yesno == "accept":
        app.complete(True, request.user)
        update_discord.delay(app.user.id)
    else:
        app.complete(False, request.user)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def groupadmin_kick(request, group_id, user_id):
    user = User.objects.get(id=user_id)
    group = Group.objects.get(id=group_id)
    group.user_set.remove(user)

    update_discord.delay(user.id)

    messages.success(request, 'Kicked %s from %s' % (user.profile.character.name, group.name))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def groupadmin_delete(request, id):
    group = Group.objects.get(id=id)
    messages.success(request, 'Deleted group %s' % group.name)
    group.delete()
    return redirect(groupadmin_index)


@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def mumbleadmin_index(request):
    server = get_server()

    context = {
        "server": server,
        "users": map(lambda x: x[1], server.getUsers().items())
    }

    o = render(request, "eveauth/mumbleadmin_index.html", context)
    server.ice_getCommunicator().destroy()
    return o



@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def mumbleadmin_kick(request, session_id):
    server = get_server()
    user = server.getUsers()[int(session_id)]
    server.kickUser(int(session_id), "Kicked via web admin")
    messages.success(request, 'Kicked %s from mumble' % user.name)

    server.ice_getCommunicator().destroy()
    return redirect(mumbleadmin_index)
