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
    radius = models.FloatField(null=True)

    def __str__(self):
        return "%s:%s" % (self.id, self.name)


class Constellation(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=100, db_index=True)
    region = models.ForeignKey(Region, related_name="constellations")
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    radius = models.FloatField(null=True)

    def __str__(self):
        return "%s:%s" % (self.id, self.name)


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
    radius = models.FloatField(null=True)
    sun = models.ForeignKey('Type')
    security_class = models.CharField(max_length=2, null=True)

    def __str__(self):
        return "%s:%s" % (self.id, self.name)


# Types
class MarketGroup(models.Model):
    id = models.IntegerField(primary_key=True)
    parent = models.ForeignKey('self', null=True, default=None, db_constraint=False)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True)
    icon_id = models.IntegerField(null=True)
    has_types = models.BooleanField()

    def __str__(self):
        return "%s:%s" % (self.id, self.name)


class Category(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, db_index=True)
    icon_id = models.IntegerField(null=True)
    published = models.BooleanField()

    def __str__(self):
        return "%s:%s" % (self.id, self.name)


class Group(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, db_index=True)
    category = models.ForeignKey(Category)
    icon_id = models.IntegerField(null=True)
    anchored = models.BooleanField()
    anchorable = models.BooleanField()
    fittable_non_singleton = models.BooleanField()
    published = models.BooleanField()

    def __str__(self):
        return "%s:%s" % (self.id, self.name)


class Type(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField()
    mass = models.FloatField(null=True)
    volume = models.FloatField(null=True)
    capacity = models.FloatField(null=True)
    published = models.BooleanField()
    market_group = models.ForeignKey(MarketGroup, null=True)
    icon_id = models.IntegerField(null=True)

    def __str__(self):
        return "%s:%s" % (self.id, self.name)


class Station(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=100, db_index=True)
    type = models.ForeignKey(Type)
    system = models.ForeignKey(System)
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()

    # Is the station a structure or an NPC station
    structure = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True, db_index=True)

    # Used to add structures
    @staticmethod
    def get_or_create(id, api):
        # Check database for station/structure
        station = Station.objects.filter(id=id).first()
        if station != None:
            return station

        # Check for structure
        if id > 71000914:
            r = api.get("/v1/universe/structures/%s/" % id)
            if r != None:
                station = Station(
                    id=id,
                    name=r['name'],
                    type_id=r['type_id'],
                    system_id=r['solar_system_id'],
                    x=r['position']['x'],
                    y=r['position']['y'],
                    z=r['position']['z']
                )
                station.save()
                return station
        else:
            # Try regular station
            r = api.get("/v2/universe/stations/%s/" % id)
            if r != None:
                station = Station(
                    id=id,
                    name=r['name'],
                    type_id=r['type_id'],
                    system_id=r['system_id'],
                    x=r['position']['x'],
                    y=r['position']['y'],
                    z=r['position']['z']
                )
                station.save()
                return station
