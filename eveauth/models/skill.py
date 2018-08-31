from django.db import models

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