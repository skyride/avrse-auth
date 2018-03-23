from django import forms
from django.contrib.auth.models import Group

from eveauth.models import GroupDetails


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