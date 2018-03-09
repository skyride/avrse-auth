from django.db import models

from .character import Character


class Role(models.Model):
    character = models.ForeignKey(Character, related_name="roles")
    name = models.CharField(max_length=128, db_index=True)


    def __str__(self):
        return "%s on %s" % (self.name, self.character.name)