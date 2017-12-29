from django.db.models import Sum
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from eveauth.models import Character


@login_required
def characters_index(request):
    context = {
        "characters": request.user.characters.all().annotate(
            total_sp=Sum('skills__skillpoints_in_skill')
        ).order_by('-total_sp'),
    }

    return render(request, "eveauth/characters.html", context)


@login_required
def characters_delete(request, id):
    character = Character.objects.get(id=id)
    if character.owner == request.user:
        token = character.token

        # Wipe character
        character.owner = None
        character.token = None
        character.save()

        # Delete social auth
        token.delete()

        # Return to characters page with success message
        messages.success(request, "Disconnected auth token for %s" % character.name)
    else:
        messages.warning(request, "You don't own %s" % character.name)

    return redirect("characters_index")
