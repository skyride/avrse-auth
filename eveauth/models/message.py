from django.db import models


class Message(models.Model):
    key = models.CharField(max_length=256, unique=True)
    value = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)