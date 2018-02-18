# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import timedelta

from django.contrib.auth.models import User, Group
from django.db import models
from django.db.models import Q
from django.utils.timezone import now

from sde.models import Type, System


class Timer(models.Model):
    STAGE_CHOICES = (
        ("AN", "Anchoring"),
        ("AR", "Armor"),
        ("ST", "Structure"),
        ("UN", "Unanchoring"),
    )

    VISIBLE_TO_LEVEL_CHOICES = (
        (0, "Non-Members"),
        (1, "Blues"),
        (2, "Members"),
    )

    SIDE_CHOICES = (
        (0, "Friendly"),
        (1, "Hostile"),
        (2, "Third-Party")
    )

    structure = models.ForeignKey(
        Type,
        related_name="timers",
        on_delete=models.CASCADE,
        limit_choices_to=Q(
                Q(group__category_id=65) |
                Q(group_id=365),
                market_group__isnull=False
            )
    )

    name = models.CharField(max_length=128, blank=True)
    owner = models.CharField(max_length=32)
    side = models.IntegerField(choices=SIDE_CHOICES, default=1)
    system = models.ForeignKey(System, related_name="timers", on_delete=models.CASCADE)

    date = models.DateTimeField(db_index=True)
    stage = models.CharField(max_length=2, choices=STAGE_CHOICES, db_index=True)

    visible_to_level = models.IntegerField(choices=VISIBLE_TO_LEVEL_CHOICES, default=2)
    visible_to_groups = models.ManyToManyField(
        Group,
        related_name="timers",
        blank=True,
        limit_choices_to=Q(
            ~Q(name__startswith="Corp:"),
            ~Q(name__startswith="Alliance:")
        )
    )

    deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(User, related_name="deleted_timers", on_delete=models.CASCADE, null=True, default=None)
    created_by = models.ForeignKey(User, related_name="timers", on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s %s-%s on %s" % (
            self.id,
            self.structure.name,
            self.stage,
            self.date
        )

    def delete(self, user):
        self.deleted = True
        self.deleted_by = user
        self.save()

    @property
    def time_until(self):
        return self.date - now()

    def user_can_edit(self, user):
        if self.user_has_access(user):
            if user.groups.filter(name__in=['admin', 'FC']).count() > 0:
                return True
            elif self.created_by == user:
                return True

        return False

    def user_has_access(self, user):
        if user.profile.level >= self.visible_to_level:
            return self.user_in_groups(user)
        else:
            return False
    
    def user_in_groups(self, user):
        if self.visible_to_groups.count() == 0:
            return True

        group_ids = user.groups.values_list('id', flat=True)
        if self.visible_to_groups.filter(
            id__in=group_ids
        ).count() > 0:
            return True

        return False