from django.contrib.auth.models import User, Group
from django.db import models


class FlarumUser(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.OneToOneField(User, related_name="flarum", on_delete=models.CASCADE)


class FlarumGroup(models.Model):
    TYPE_CHOICES = (
        ("access_level", "Access Level"),
        ("corp", "Corp"),
        ("alliance", "Alliance"),
        ("group", "Group"),
    )

    id = models.IntegerField(primary_key=True)
    type = models.CharField(choices=TYPE_CHOICES, max_length=32, db_index=True)
    name = models.CharField(max_length=128, db_index=True)
    group = models.ForeignKey(Group, null=True, default=None)