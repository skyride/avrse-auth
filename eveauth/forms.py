from django import forms
from django.contrib.auth.models import Group

from eveauth.models import GroupDetails, Requirement


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = [
            "name"
        ]


class GroupDetailsForm(forms.ModelForm):
    class Meta:
        model = GroupDetails
        fields = [
            "is_open",
            "can_apply",
            "access_level",
            "mumble",
            "forum",
            "discord"
        ]


class CharacterVisibleToForm(forms.Form):
    VISIBLE_FOR_CHOICES = (
        (0, "----"),
        (1, "1 hour"),
        (3, "3 hours"),
        (12, "12 hours"),
        (24, "1 day"),
        (72, "3 days"),
        (168, "7 days"),
    )
    VISIBLE_TO_CHOICES = (
        (0, "Anyone"),
        (2, "Members Only")
    )

    visible_for = forms.ChoiceField(
        label="Visible For",
        required=True,
        choices=VISIBLE_FOR_CHOICES,
    )
    visible_to = forms.ChoiceField(
        label="Visible To",
        required=True,
        choices=VISIBLE_TO_CHOICES,
    )


class RequirementForm(forms.ModelForm):
    class Meta:
        model = Requirement
        fields = [
            "name",
            "description",
            "enabled"
        ]