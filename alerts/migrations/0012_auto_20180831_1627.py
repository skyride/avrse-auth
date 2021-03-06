# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-08-31 16:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alerts', '0011_auto_20180505_2111'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webhook',
            name='event',
            field=models.CharField(choices=[(b'structure_reinforce', b'Structure Reinforce'), (b'structure_anchoring', b'Structure Anchor/Unanchor'), (b'low_fuel_filtered', b'Low Fuel (Filtered)'), (b'low_fuel_all', b'Low Fuel (All)'), (b'structure_attacked', b'Structured Attacked'), (b'group_app', b'New Group Application'), (b'character_added', b'Character Added'), (b'character_deleted', b'Character Deleted'), (b'character_expired', b'Character Expired'), (b'character_joined', b'Character Joined Corp'), (b'character_left', b'Character Left Corp')], db_index=True, max_length=64, verbose_name=b'Event'),
        ),
    ]
