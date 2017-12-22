# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# ESI Scope
class Scope(models.Model):
    name = models.CharField(max_length=128, db_index=True)
    description = models.TextField()

    def __str__(self):
        return self.name
