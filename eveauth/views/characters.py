from datetime import timedelta

from django.db.models import Sum
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils.timezone import now

from eveauth.models import Character, Asset
from eveauth.forms import CharacterVisibleToForm

@login_required
def characters_index(request):
    context = {
        "characters": request.user.characters.all().annotate(
            total_sp=Sum('skills__skillpoints_in_skill')
        ).order_by('-total_sp'),
    }

    return render(request, "eveauth/characters.html", context)


@login_required
def characters_view(request, id):
    char = request.user.characters.filter(id=id)

    # Check if this char is member visible
    if not char.exists():
        char = Character.objects.filter(
            id=id,
            token__isnull=False,
            visible_until__gte=now(),
            visible_to__lte=request.user.profile.level
        )

    return _characters_view(request, char)


@login_required
def characters_view_anonymous(request, key):
    char = request.user.characters.filter(
        public_key=key,
        public_until__gte=now()
    )
    return _characters_view(request, char)


def _characters_view(request, char):
    char = char.prefetch_related(
            'skills',
            'corp',
            'alliance',
            'home',
            'ship',
            'implants',
            'implants__type',
            'clones',
            'clones__implants',
            'clones__implants__type'
        ).annotate(
            total_sp=Sum('skills__skillpoints_in_skill')
        ).first()

    # Handle visibility form submission
    if request.method == "POST":
        form = CharacterVisibleToForm(request.POST)
        if form.is_valid():
             char.visible_to = form.cleaned_data['visible_to']
             char.visible_until = now() + timedelta(hours=int(form.cleaned_data['visible_for']))
             char.save()

    skill_groups = char.skills.values_list(
        'type__group__name',
        flat=True
    ).order_by(
        'type__group__name'
    ).distinct()

    skills = []
    for group in skill_groups:
        group_skills = char.skills.filter(
            type__group__name=group
        ).prefetch_related(
            'type',
            'type__attributes'
        ).order_by(
            'type__name'
        )
        total = group_skills.aggregate(
            total=Sum('skillpoints_in_skill')
        )['total']

        skills.append(
            (
                group,
                group_skills,
                total
            )
        )

    form = CharacterVisibleToForm(
        initial={
            "visible_to": 2,
            "visible_for": 168
        }
    )

    context = {
        "character": char,
        "skill_groups": skills,
        "visibility_form": form,
        "admin": request.user.groups.filter(name="admin").exists(),
        "now": now()
    }

    return render(request, "eveauth/character_view.html", context)


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


@login_required
def assets_index(request):
    user = request.user

    context = {
        "view_ship": "assets_viewship",
        "user": user,
        "assets": Asset.objects.filter(
                character__owner=user,
                type__group__category__id=6,
                singleton=True,
                system__isnull=False
            ).exclude(
                type__group__id__in=[
                    29,             # Capsule
                    237,            # Noobship
                ]
            ).prefetch_related(
                'system',
                'system__region',
                'character',
                'type',
                'type__group'
            ).order_by(
                'system__region__name',
                'system__name',
                'character__name',
                '-type__mass',
                'type__group__name',
                'type__name'
            ).all()
    }

    return render(request, "eveauth/view_ships.html", context)


@login_required
def assets_viewship(request, id):
    ship = Asset.objects.get(id=id)

    if ship.character.owner == request.user:
        context = {
            "ship": ship,
            "view_ship": "assets_viewship"
        }
        return render(request, "eveauth/view_ship.html", context)
