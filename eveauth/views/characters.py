from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required
def characters_index(request):
    context = {}

    return render(request, "eveauth/characters.html", context)
