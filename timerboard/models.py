# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

from sde.models import Type, System


class Timer(models.Model):
    STAGE_CHOICES = (
        ("AR", "Armor"),
        ("ST", "Structure"),
    )

    structure = models.ForeignKey(Type, related_name="timers", on_delete=models.CASCADE)
    system = models.ForeignKey(System, related_name="timers", on_delete=models.CASCADE)

    date = models.DateTimeField(db_index=True)
    stage = models.CharField(max_length=2, choices=STAGE_CHOICES, db_index=True)

    created_by = models.ForeignKey(User, related_name="timers", on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)