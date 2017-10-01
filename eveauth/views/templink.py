from __future__ import unicode_literals

import json
from datetime import timedelta

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.utils.crypto import get_random_string
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from django.db import IntegrityError

from eveauth.models import Templink, TemplinkUser
from eveauth.tasks import purge_templink_users



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


# Admin page to create temp link
@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def templink_create(request):
    return render(request, "eveauth/templink_create.html")


# Form submission to create templink
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


# Admin page link to disable templink
@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def templink_disable(request, id):
    templink = Templink.objects.get(id=id)
    templink.active = False
    templink.save()

    #CODE TO KICK PEOPLE GOES HERE
    purge_templink_users(templink.id)

    return redirect(templink_index)


# Page the user lands on when they click a temp link
def templink_landing(request, link):
    templink = Templink.objects.filter(
        Q(expires__gte=timezone.now()) | Q(expires__isnull=True),
        link=link,
        active=True
    )
    if not templink.exists():
        return render(request, "eveauth/templink_invalid.html")
    templink = templink.first()

    context = {
        "templink": templink
    }
    return render(request, "eveauth/templink_landing.html", context)


# Form submission page
def templink_landing_submit(request, link):
    templink = Templink.objects.filter(
        Q(expires__gte=timezone.now()) | Q(expires__isnull=True),
        link=link,
        active=True
    )
    if not templink.exists():
        return render(request, "eveauth/templink_invalid.html")
    templink = templink.first()

    try:
        user = TemplinkUser(
            templink=templink,
            name=request.POST.get("name"),
            password=get_random_string(32)
        )
        user.save()
    except IntegrityError:
        messages.warning(request, "That name was already taken.")
        return redirect(templink_landing, link)

    context = {
        "user": user,
        "templink": templink,
        "mumble_host": settings.MUMBLE_HOST,
        "mumble_port": settings.MUMBLE_PORT,
    }
    return render(request, "eveauth/templink_submit.html", context)
