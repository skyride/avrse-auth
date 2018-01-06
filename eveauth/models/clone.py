from django.db import models

from character import Character
from sde.models import Station, Type


class Clone(models.Model):
    id = models.BigIntegerField(primary_key=True)
    character = models.ForeignKey(Character, related_name="clones")
    name = models.CharField(max_length=100, default="")
    location = models.ForeignKey(Station, related_name="jump_clones")

    def __str__(self):
        return "%s:%s" % (
            self.name,
            location.name
        )


class CloneImplant(models.Model):
    clone = models.ForeignKey(Clone, related_name="implants")
    type = models.ForeignKey(Type)

    @property
    def slot(self):
        return self.type.attributes.get(attribute_id=331).value


    def __str__(self):
        return "%s:%s" % (
            self.slot,
            self.type.name
        )
