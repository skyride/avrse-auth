from datetime import datetime
from django.db import models
from django.contrib.auth.models import User, Group


class GroupApp(models.Model):
    user = models.ForeignKey(User, related_name="group_apps", on_delete=models.CASCADE)
    group = models.ForeignKey(Group, related_name="apps", on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now=True, db_index=True)

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
