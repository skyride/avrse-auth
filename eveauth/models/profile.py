from django.contrib.auth.models import User
from social_django.models import UserSocialAuth
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from character import Character
from corporation import Corporation
from alliance import Alliance

from eveauth.tasks import update_groups


class Profile(models.Model):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)

    level = models.IntegerField(default=0)
    mumble_password = models.CharField(max_length=128, null=True, blank=True)

    character = models.ForeignKey(Character, null=True)
    corporation = models.ForeignKey(Corporation, null=True)
    alliance = models.ForeignKey(Alliance, null=True)

    forum_id = models.IntegerField(null=True)
    forum_username = models.CharField(max_length=128, null=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
