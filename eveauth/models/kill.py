from django.db import models

from character import Character
from sde.models import System, Type


class Kill(models.Model):
    id = models.BigIntegerField(primary_key=True)
    victim = models.ForeignKey(Character, related_name="losses")
    killers = models.ManyToManyField(Character, related_name="kills")
    ship = models.ForeignKey(Type, related_name="losses")
    system = models.ForeignKey(System, related_name="kills")
    price = models.DecimalField(max_digits=16, decimal_places=2, default=0, db_index=True)
    date = models.DateTimeField(db_index=True)
