import requests
import json

from django.db import models
from django.conf import settings


def simple_message(message):
    return {
        "content": message
    }


class Webhook(models.Model):
    NAME_CHOICES = (
        ('structure_reinforce', "Structure Reinforce"),
        ("low_fuel", "Low Fuel")
    )

    event = models.CharField(max_length=64, db_index=True, choices=NAME_CHOICES)
    url = models.CharField(max_length=512)
    active = models.BooleanField(default=True)


    @staticmethod
    def send(event, message):
        hooks = Webhook.objects.filter(event=event)
        if not hooks.exists():
            return False

        for hook in hooks.filter(active=True).all():
            requests.post(
                hook.url,
                json=message
            ).content
        return True
