# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-03-11 03:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eveauth', '0049_auto_20180311_0329'),
    ]

    operations = [
        migrations.AddField(
            model_name='structure',
            name='state_timer_end',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='structure',
            name='state_timer_start',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]
