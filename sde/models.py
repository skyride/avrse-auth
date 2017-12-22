# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models


# Map
class Region(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=100, db_index=True)
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    radius = models.FloatField()


class Constellation(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=100, db_index=True)
    region = models.ForeignKey(Region, related_name="constellations")
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    radius = models.FloatField()


class System(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=100, db_index=True)
    region = models.ForeignKey(Region, related_name="systems")
    constellation = models.ForeignKey(Constellation, related_name="systems")
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    luminosity = models.FloatField()
    border = models.BooleanField()
    fringe = models.BooleanField()
    corridor = models.BooleanField()
    hub = models.BooleanField()
    international = models.BooleanField()
    security = models.FloatField()
    radius = models.FloatField()
    sun = models.ForeignKey('Type')
    security_class = models.CharField(max_length=2)


# Types
class MarketGroup(models.Model):
    id = models.IntegerField(primary_key=True)
    parent = models.ForeignKey('self', null=True, default=None, db_constraint=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon_id = models.IntegerField(null=True)
    hasTypes = models.BooleanField()


class Category(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, db_index=True)
    icon_id = models.IntegerField(null=True)
    published = models.BooleanField()


class Group(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, db_index=True)
    category = models.ForeignKey(Category)
    icon_id = models.IntegerField(null=True)
    anchored = models.BooleanField()
    anchorable = models.BooleanField()
    fittableNonSingleton = models.BooleanField()
    published = models.BooleanField()


class Type(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField()
    mass = models.FloatField(null=True)
    volume = models.FloatField(null=True)
    capacity = models.FloatField(null=True)
    published = models.BooleanField()
    market_group = models.ForeignKey(MarketGroup)
    icon_id = models.IntegerField(null=True)
