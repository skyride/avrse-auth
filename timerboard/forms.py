from datetime import timedelta

from django import forms
from django.contrib.auth.models import Group
from django.db.models import Q
from django.utils.timezone import now

from timerboard.models import Timer
from sde.models import Type, System


class TimerForm(forms.ModelForm):
    days = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'class':'form-control',
                'min': 1,
                'max': 31
            },
        )
    )
    hours = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'class':'form-control',
                'min': 1,
                'max': 23
            },
        )
    )
    minutes = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'class':'form-control',
                'min': 1,
                'max': 59
            },
        )
    )

    def clean(self):
        cleaned_data = super(TimerForm, self,).clean()

        cleaned_data['date'] = now() + timedelta(
            days=self.cleaned_data['days'],
            hours=self.cleaned_data['hours'],
            minutes=self.cleaned_data['minutes']
        )

        self.instance.date = cleaned_data['date']

        return cleaned_data

    class Meta:
        model = Timer
        fields = (
            'structure',
            'stage',
            'name',
            'owner',
            'side',
            'system',
            'days',
            'hours',
            'minutes',
            'visible_to_level',
            'visible_to_groups'
        )