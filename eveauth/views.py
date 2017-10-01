from __future__ import unicode_literals

import json
from datetime import timedelta

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.utils.crypto import get_random_string
from django.conf import settings
from django.utils import timezone

from eveauth.models import Templink


def home(request):
    if not request.user.is_authenticated():
        return render(request, "eveauth/home.html")
    else:
        return redirect(services)


@login_required
def services(request):
    context = {
        "mumble_host": settings.MUMBLE_HOST,
        "mumble_port": settings.MUMBLE_PORT,
    }

    return render(request, "eveauth/services.html", context)


@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def templink_index(request):
    context = {
        "templinks": Templink.objects.order_by(
            "-active",
            "-created"
        ).prefetch_related(
            "created_by"
        )
    }

    return render(request, "eveauth/templink_index.html", context)


@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def templink_create(request):
    return render(request, "eveauth/templink_create.html")


@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def templink_submit(request):
    templink = Templink(
        link=get_random_string(12),
        tag=request.POST.get("tag"),
        description=request.POST.get("description"),
        created_by=request.user
    )

    duration = request.POST.get("duration")
    if duration != "forever":
        templink.expires = timezone.now() + timedelta(0, int(duration))
    templink.save()

    return redirect(templink_index)


@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def templink_disable(request, id):
    templink = Templink.objects.get(id=id)
    templink.active = False
    templink.save()

    #CODE TO KICK PEOPLE GOES HERE

    return redirect(templink_index)


@login_required
def update_mumble_password(request):
    profile = request.user.profile

    hasher = PBKDF2PasswordHasher()
    password = request.POST.get("mumble_password")
    password = hasher.encode(password, get_random_string(12))
    profile.mumble_password = password

    profile.save()
    return redirect(services)
