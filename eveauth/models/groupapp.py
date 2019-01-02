from datetime import datetime
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group


class GroupApp(models.Model):
    user = models.ForeignKey(User, related_name="group_apps", on_delete=models.CASCADE)
    group = models.ForeignKey(Group, related_name="apps", on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_updated = models.DateTimeField(auto_now=True, db_index=True)

    accepted = models.NullBooleanField(default=None)
    completed = models.DateTimeField(null=True, default=None)
    completed_by = models.ForeignKey(User, null=True, default=None, on_delete=models.CASCADE)


    def complete(self, accepted, completer):
        self.accepted = accepted
        self.completed = datetime.now()
        self.completed_by = completer
        self.save()

        if accepted:
            self.group.user_set.add(self.user)


@receiver(post_save, sender=GroupApp)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Generate group application event
        from alerts.models import Webhook
        from alerts.embeds import group_app
        Webhook.send(
            "group_app",
            group_app(instance)
        )