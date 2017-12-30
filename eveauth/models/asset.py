from django.db import models

from eveauth.models.character import Character
from sde.models import Type, System, Station


class Asset(models.Model):
    id = models.BigIntegerField(primary_key=True)
    character = models.ForeignKey(Character, related_name="assets")
    parent = models.ForeignKey('self', null=True, default=None, db_constraint=False, related_name="items")

    type = models.ForeignKey(Type)
    flag = models.CharField(max_length=64)

    quantity = models.IntegerField(default=0)
    raw_quantity = models.IntegerField(default=0)
    singleton = models.BooleanField()

    system = models.ForeignKey(System, null=True, default=None)
    station = models.ForeignKey(Station, null=True, default=None)
    name = models.CharField(max_length=64, null=True, default=None)
