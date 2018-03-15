from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from alerts.models import Webhook


@login_required
@user_passes_test(lambda x: x.groups.filter(name__in=["admin"]).exists())
def settings_webhooks_index(request):
    context = {
        "webhooks": Webhook.objects.order_by('event').all()
    }

    return render(request, "eveauth/settings/webhooks.html", context)