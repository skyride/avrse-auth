import yaml

from django.db import models

from eveauth.models.character import Character


class Notification(models.Model):
    id = models.BigIntegerField(primary_key=True)
    characters = models.ManyToManyField(Character, related_name="notifications")
    text = models.TextField(default="")
    sender_id = models.IntegerField(null=True, default=None)
    sender_type = models.CharField(max_length=64, db_index=True)
    date = models.DateTimeField(null=True, default=None)
    type = models.CharField(max_length=64, db_index=True)

    # The text field is actually just YAML so we can parse it and return the dict
    @property
    def data(self):
        return yaml.load(self.text)


    def __str__(self):
        return "%s:%s" % (
            self.id,
            self.type
        )