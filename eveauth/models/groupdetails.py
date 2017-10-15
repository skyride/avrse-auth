from django.db import models
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver


class GroupDetails(models.Model):
    group = models.OneToOneField(Group, related_name="details", on_delete=models.CASCADE)

    is_open = models.BooleanField(default=False)
    can_apply = models.BooleanField(default=False)

    mumble = models.BooleanField(default=True)
    forum = models.BooleanField(default=False)
    discord = models.BooleanField(default=False)


@receiver(post_save, sender=Group)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        GroupDetails.objects.create(group=instance)
    else:
        if not hasattr(instance, 'details'):
            GroupDetails.objects.create(group=instance)
