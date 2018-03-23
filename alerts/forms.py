from django import forms

from alerts.models import Webhook


class WebhookForm(forms.ModelForm):
    class Meta:
        model = Webhook
        fields = [
            "event",
            "url",
            "notify",
            "active"
        ]