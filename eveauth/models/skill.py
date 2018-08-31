from datetime import datetime

from django.db import models
from django.utils.timezone import now

from eveauth.models.character import Character
from sde.models import Type


class Skill(models.Model):
    character = models.ForeignKey(Character, related_name="skills")
    type = models.ForeignKey(Type)
    trained_skill_level = models.IntegerField()
    active_skill_level = models.IntegerField()
    skillpoints_in_skill = models.IntegerField()

    @property
    def rank(self):
        return int(self.type.attributes.get(attribute_id=275).value)


class SkillTraining(models.Model):
    character = models.ForeignKey(Character, related_name="training_skills")
    type = models.ForeignKey(Type)

    start_sp = models.IntegerField(default=0)
    end_sp = models.IntegerField(default=0)
    training_to_level = models.IntegerField(default=0)
    position = models.IntegerField(default=0, db_index=True)

    starts = models.DateTimeField(null=True, default=None, db_index=True)
    ends = models.DateTimeField(null=True, default=None, db_index=True)

    class Meta:
        ordering = ('position', )

    def percentage_complete(self):
        total_seconds = (self.ends - self.starts).total_seconds()
        current_seconds = (self.ends - now()).total_seconds()
        return 100.0 / float(total_seconds) * current_seconds

    def time_left(self):
        return self.ends - self.starts