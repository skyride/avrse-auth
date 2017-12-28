from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required
def characters_index(request):
    context = {
        "characters": request.user.characters.all().order_by('name'),
    }

    return render(request, "eveauth/characters.html", context)
