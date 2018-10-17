from datetime import timedelta

from django import forms
from django.contrib.auth.models import Group
from django.db.models import Q
from django.utils.timezone import now

from timerboard.models import Timer
from sde.models import Type, System


class TimerForm(forms.ModelForm):
    days = forms.IntegerField(
        widget=forms.NumberInput()
    )
    hours = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'min': 0,
                'max': 23
            },
        )
    )
    minutes = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'min': 0,
                'max': 59
            },
        )
    )

    def clean(self):
        cleaned_data = super(TimerForm, self,).clean()

        cleaned_data['date'] = now() + timedelta(
            days=cleaned_data['days'],
            hours=cleaned_data['hours'],
            minutes=cleaned_data['minutes']
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


class StructureExitForm(forms.Form):
    EXIT_DAY_CHOICES = (
        (1, "Monday"),
        (2, "Tuesday"),
        (3, "Wednesday"),
        (4, "Thursday"),
        (5, "Friday"),
        (6, "Saturday"),
        (7, "Sunday")
    )
    LOCATION_CHOICES = (
        (0.5, "W-Space"),
        (2.5, "Lowsec/Nullsec"),
        (5.5, "Highsec")
    )
    IS_POWERED_CHOICES = (
        (1, "Online"),
        (0, "Low Power")
    )

    exit_day = forms.ChoiceField(choices=EXIT_DAY_CHOICES)
    exit_time = forms.ChoiceField(choices=[(i, "{:0>2d}".format(i)+":00") for i in range(0, 24)])
    location = forms.ChoiceField(choices=LOCATION_CHOICES)
    is_powered = forms.ChoiceField(choices=IS_POWERED_CHOICES)