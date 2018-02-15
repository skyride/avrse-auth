# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, reverse
from django.utils.timezone import now

from timerboard.forms import TimerForm
from timerboard.models import Timer


@login_required
def index(request):
    context = {
        "timers": filter(
                lambda x: x.user_in_groups(request.user),
                Timer.objects.filter(
                    date__gte=now() - timedelta(minutes=60),
                    visible_to_level__lte=request.user.profile.level,
                    deleted=False
                ).order_by(
                    'date'
                )
            ),
        "archive": filter(
                lambda x: x.user_in_groups(request.user),
                Timer.objects.filter(
                    date__lt=now() - timedelta(minutes=60),
                    date__gt=now() - timedelta(days=30),
                    visible_to_level__lte=request.user.profile.level,
                    deleted=False
                ).order_by(
                    '-date'
                )
            ),
        "now": now()
    }

    return render(request, "timerboard/index.html", context)


@login_required
def delete(request, id):
    timer = Timer.objects.get(id=id)

    if timer.user_can_edit(request.user):
        timer.delete(request.user)
        messages.success(request, "Successfully deleted timer")
        return redirect("timerboard:index")


@login_required
def edit(request, timer=None):
    if request.method == "POST":
        form = TimerForm(request.POST)
        form.instance.created_by = request.user
        form.save()
        messages.success(request, "Successfully updated timer")
        return redirect("timerboard:edit", form.instance.id)

    if timer == None:
        method = "Add Timer"
        form = TimerForm()
    else:
        method = "Edit Timer"
        timer = Timer.objects.get(id=timer)
        diff = timer.date - now()
        days = diff.days

        form = TimerForm(
            instance=timer,
            initial={
                'days': diff.days,
                'hours': int((diff.total_seconds() % 86400) // 3600),
                'minutes': int((diff.total_seconds() % 3600) / 60)
            }
        )

    context = {
        "method": method,
        "form": form
    }

    return render(request, "timerboard/edit.html", context)


@login_required
def add(request):
    return edit(request)