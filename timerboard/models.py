# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import timedelta
from django.utils.timezone import now

from django.contrib.auth.models import User, Group
from django.db import models

from sde.models import Type, System


class Timer(models.Model):
    STAGE_CHOICES = (
        ("AR", "Armor"),
        ("ST", "Structure"),
    )

    VISIBLE_TO_LEVEL_CHOICES = (
        (0, "Non-Members"),
        (1, "Blues"),
        (2, "Members"),
    )

    SIDE_CHOICES = (
        (0, "Friendly"),
        (1, "Hostile"),
        (2, "Third-Party")
    )

    structure = models.ForeignKey(Type, related_name="timers", on_delete=models.CASCADE)
    name = models.CharField(max_length=128, blank=True)
    owner = models.CharField(max_length=32)
    side = models.IntegerField(choices=SIDE_CHOICES, default=1)
    system = models.ForeignKey(System, related_name="timers", on_delete=models.CASCADE)

    date = models.DateTimeField(db_index=True)
    stage = models.CharField(max_length=2, choices=STAGE_CHOICES, db_index=True)

    visible_to_level = models.IntegerField(choices=VISIBLE_TO_LEVEL_CHOICES, default=2)
    visible_to_groups = models.ManyToManyField(Group, related_name="timers", blank=True)

    created_by = models.ForeignKey(User, related_name="timers", on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s %s-%s on %s" % (
            self.id,
            self.structure.name,
            self.stage,
            self.date
        )

    @property
    def time_until(self):
        return now() - self.date