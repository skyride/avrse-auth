# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-02-15 15:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timerboard', '0003_auto_20180215_1404'),
    ]

    operations = [
        migrations.AddField(
            model_name='timer',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
    ]