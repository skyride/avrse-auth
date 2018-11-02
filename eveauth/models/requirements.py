from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from sde.models import Type


class Requirement(models.Model):
    """
    Represents a set of required skills grouped into something meaningful e.g. "Doctrine A - DPS Loki", "Scanning Alt", etc
    """
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    enabled = models.BooleanField(default=True)


class RequirementSkill(models.Model):
    """
    Represents a single skill in a requirement
    """
    requirement = models.ForeignKey(Requirement, related_name="skills")
    skill = models.ForeignKey(Type, related_name="requirement_skills")
    required_level = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    recommended_level = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])