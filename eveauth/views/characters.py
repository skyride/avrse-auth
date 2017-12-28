from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required
def characters_index(request):
    context = {
        "characters": request.user.characters.all(),

    }

    return render(request, "eveauth/characters.html", context)
