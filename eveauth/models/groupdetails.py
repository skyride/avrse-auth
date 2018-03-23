from django.db import models
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver


class GroupDetails(models.Model):
    ACCESS_LEVEL_CHOICES = (
        (0, 'Non-Members'),
        (1, 'Blues'),
        (2, "Members"),
    )

    group = models.OneToOneField(Group, related_name="details", on_delete=models.CASCADE)

    is_open = models.BooleanField(default=False)
    can_apply = models.BooleanField(default=False)
    access_level = models.IntegerField(default=2, choices=ACCESS_LEVEL_CHOICES)

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
