from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from alerts.models import Webhook
from alerts.forms import WebhookForm


@login_required
@user_passes_test(lambda x: x.groups.filter(name__in=["admin"]).exists())
def settings_webhooks_index(request):
    # Save any changes
    if request.method == "POST":
        if "delete" in request.POST:
            Webhook.objects.get(id=int(request.POST.get("delete"))).delete()
        else:
            if request.POST.get("id"):
                webhook = Webhook.objects.get(id=request.POST.get("id"))
            else:
                webhook = Webhook()
            form = WebhookForm(request.POST, instance=webhook)
            form.save()

    webhooks = [WebhookForm(instance=webhook) for webhook in Webhook.objects.order_by('event')]
    webhooks.append(WebhookForm())

    context = {
        "webhooks": webhooks
    }

    return render(request, "eveauth/settings/webhooks.html", context)