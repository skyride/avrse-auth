# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-03-23 17:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eveauth', '0057_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupdetails',
            name='access_level',
            field=models.IntegerField(choices=[(0, b'Non-Members'), (1, b'Blues'), (2, b'Members')], default=2),
        ),
    ]
