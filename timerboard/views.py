# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render



def index(request):
    return render(request, "timerboard/index.html")