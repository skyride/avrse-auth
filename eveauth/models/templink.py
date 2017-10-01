from django.db import models
from django.contrib.auth.models import User


class Templink(models.Model):
    link = models.CharField(max_length=12, default="", db_index=True)
    tag = models.CharField(max_length=32)
    description = models.TextField(default="")
    active = models.BooleanField(default=True)
    expires = models.DateTimeField(null=True, db_index=True)
    created = models.DateTimeField(auto_now=True, db_index=True)
    created_by = models.ForeignKey(User)
