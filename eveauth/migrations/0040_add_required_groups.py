# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2017-12-30 16:46
from __future__ import unicode_literals

from django.db import migrations, models


def add_groups(*args, **kwargs):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('eveauth', '0039_auto_20171230_1646'),
    ]

    operations = [
        migrations.RunPython(add_groups),
    ]
