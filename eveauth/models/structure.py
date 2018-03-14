from django.db import models

from corporation import Corporation
from sde.models import Station, Type, System


class Structure(models.Model):
    REINFORCE_WEEKDAY_CHOICES = (
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday")
    )

    id = models.BigIntegerField(primary_key=True)
    corporation = models.ForeignKey(Corporation, related_name="structures")
    type = models.ForeignKey(Type, related_name="structures")
    station = models.OneToOneField(Station, related_name="corp_structure")
    system = models.ForeignKey(System, related_name="structures")
    profile_id = models.IntegerField()

    state = models.CharField(max_length=64)
    fuel_expires = models.DateTimeField(null=True, default=None)
    reinforce_weekday = models.IntegerField(choices=REINFORCE_WEEKDAY_CHOICES)
    reinforce_hour = models.IntegerField()
    state_timer_start = models.DateTimeField(null=True, default=None)
    state_timer_end = models.DateTimeField(null=True, default=None)

    fuel_notifications = models.BooleanField(default=False)

    def __str__(self):
        return "%s:%s:%s" % (
            self.id,
            self.type.name,
            self.station.name
        )


class Service(models.Model):
    structure = models.ForeignKey(Structure, related_name="services")
    name = models.CharField(max_length=64)
    state = models.BooleanField(default=False)

    def __str__(self):
        return "%s (%s)" % (
            self.name,
            self.state
        )