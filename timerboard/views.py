# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.utils.timezone import now

from timerboard.models import Timer



def index(request):
    context = {
        "timers": Timer.objects.filter(
                date__gte=now() - timedelta(minutes=60)
            ).order_by(
                'date'
            ),
        "archive": Timer.objects.filter(
                date__lt=now() - timedelta(minutes=60),
                date__gt=now() - timedelta(days=30)
            ).order_by(
                '-date'
            ),
        "now": now()
    }

    return render(request, "timerboard/index.html", context)