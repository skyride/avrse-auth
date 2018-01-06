from django.db import models

from sde.models import Type
from character import Character


class Implant(models.Model):
    character = models.ForeignKey(Character, related_name="implants")
    type = models.ForeignKey(Type, related_name="implants")

    @property
    def slot(self):
        return self.type.attributes.get(attribute_id=331).value


    def __str__(self):
        return "%s:%s" % (
            self.slot,
            self.type.name
        )
