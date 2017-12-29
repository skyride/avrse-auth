from django.db import models

from sde.models import Type, System, Station


class Asset(models.Model):
    id = models.BigIntegerField(primary_key=True)
    parent = models.ForeignKey('self', null=True, default=None, db_constraint=False)

    type = models.ForeignKey(Type)
    flag = models.CharField(max_length=64)

    quantity = models.IntegerField(default=0)
    raw_quantity = models.IntegerField(default=0)
    singleton = models.BooleanField()

    system = models.ForeignKey(System)
    station = models.ForeignKey(Station, null=True, default=None)
    name = models.CharField(max_length=64, null=True, default=None)
