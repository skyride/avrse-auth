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
def update_mumble_password(request):
    profile = request.user.profile

    hasher = PBKDF2PasswordHasher()
    password = request.POST.get("mumble_password")
    password = hasher.encode(password, get_random_string(12))
    profile.mumble_password = password

    profile.save()
    return redirect(services)
