from django.contrib.auth.models import User, Group
from django.db import models


class FlarumGroup(models.Model):
    TYPE_CHOICES = (
        ("access_level", "Access Level"),
        ("corp", "Corp"),
        ("alliance", "Alliance"),
        ("group", "Group"),
        ("forum_group", "Forum Group")
    )

    id = models.IntegerField(primary_key=True)
    type = models.CharField(choices=TYPE_CHOICES, max_length=32, db_index=True)
    name_singular = models.CharField(max_length=128, db_index=True)
    name_plural = models.CharField(max_length=128, db_index=True)
    group = models.ForeignKey(Group, null=True, default=None)

    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s/%s" % (self.name_singular, self.name_plural)


class FlarumUser(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=128, db_index=True)
    email = models.CharField(max_length=255, db_index=True)
    user = models.OneToOneField(User, related_name="flarum", null=True, default=None, on_delete=models.CASCADE)
    groups = models.ManyToManyField(FlarumGroup, related_name="users")
    last_seen_time = models.DateTimeField(db_index=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username