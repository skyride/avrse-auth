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

from eveauth.tasks import get_server


@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def mumbleadmin_index(request):
    server = get_server()

    context = {
        "server": server,
        "users": server.getUsers().items()
    }

    return render(request, "eveauth/mumbleadmin_index.html", context)


def mumbleadmin_kick(request, session_id):
    server = get_server()
    server.kickUser(int(session_id), "Kicked via web admin")

    return redirect(mumbleadmin_index)
