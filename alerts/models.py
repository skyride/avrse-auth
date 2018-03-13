# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Webhook(models.Model):
    NAME_CHOICES = (
        ('structure_reinforce', "Structure Reinforce"),
    )

    name = models.CharField(max_length=64, db_index=True, choices=NAME_CHOICES)
    url = models.CharField(max_length=512)
    active = models.BooleanField(default=True)