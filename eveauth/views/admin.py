from __future__ import unicode_literals

import json
import requests
import math
from datetime import timedelta

from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator
from django.utils.crypto import get_random_string
from django.conf import settings
from django.utils import timezone
from django.db.models import Q, Count, Sum
from django.db import IntegrityError

from eveauth.esi import ESI
from eveauth.models import GroupApp, Character, Corporation, Alliance, Asset, Kill
from eveauth.tasks import get_server, update_groups, spawn_groupupdates, update_discord
from eveauth.discord.api import DiscordAPI


@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def corpaudit_search(request):
    search = request.GET.get("search", False)
    if search == False:
        return render(request, "eveauth/corpaudit_search.html", {})

    # Get corp info for live search
    corps = Corporation.objects.filter(
        Q(name__istartswith=search)
        | Q(ticker__istartswith=search),
        characters__owner__isnull=False,
        id__gt=1001000
    ).annotate(
        chars=Count('characters')
    ).filter(
        chars__gt=0
    ).order_by(
        '-chars'
    ).all()

    api = ESI()
    def get_member_count(id):
        r = api.get("/v4/corporations/%s/" % id)
        return r['member_count']

    corps = map(
        lambda x: {
            "id": x.id,
            "name": x.name,
            "tickers": x.ticker,
            "chars": x.chars,
            "members": get_member_count(x.id)
        },
        corps
    )

    context = {
        "search": search,
        "corps": corps
    }

    return render(request, "eveauth/corpaudit_search.html", context)


@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def corpaudit_view(request, id):
    r = ESI().get("/v4/corporations/%s/" % id)
    corp = Corporation.objects.prefetch_related(
        'characters',
        'characters__owner'
    ).get(id=id)

    # Populate corp object with extra data
    corp.member_count = r['member_count']
    corp.ceo = Character.get_or_create(r['ceo_id'])
    corp.description = r['description']
    corp.tax_rate = r['tax_rate']
    corp.founder = Character.get_or_create(r['creator_id'])
    if "alliance_id" in r:
        corp.alliance = Alliance.get_or_create(r['alliance_id'])

    # Call evewho
    r = requests.get("https://evewho.com/api.php?type=corplist&id=%s&page=0" % id).json()
    chars = r['characters']
    if int(r['info']['memberCount']) > 200:
        for i in range(1, int(math.ceil((int(r['info']['memberCount'])) / 200) + 1)):
            r = requests.get("https://evewho.com/api.php?type=corplist&id=%s&page=%s" % (id, i)).json()
            chars = chars + r['characters']

    for char in chars:
        try:
            char['char'] = Character.objects.get(
                id=char['character_id'],
                owner__isnull=False
            )
        except Exception:
            pass

    context = {
        "corp": corp,
        "char_count": corp.characters.filter(
                owner__isnull=False
            ).count(),
        "chars": sorted(chars, key=lambda x: x['name'])
    }

    return render(request, "eveauth/corpaudit_view.html", context)


@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def registeredusers_index(request, page=1, order_by=""):
    if order_by == None:
        order_by = 'last_login'

    order_by_dict = {
        "name": "profile__character__name",
        "corp": "profile__corporation__name",
        "alliance": "profile__alliance__name",
        "access_level": "profile__level",
        "last_login": "-last_login",
        "chars": "-chars",
    }

    users = User.objects.prefetch_related(
        "profile",
        "profile__character",
        "profile__corporation",
        "profile__alliance"
    ).annotate(
        chars=Count('characters')
    ).order_by(
        order_by_dict[order_by],
        "profile__corporation__name"
    ).all()
    paginator = Paginator(users, 40)

    context = {
        "users": paginator.page(page),
        "order_by": order_by
    }

    return render(request, "eveauth/registeredusers_index.html", context)



@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def user_updategroups(request, id):
    update_groups.delay(id)
    user = User.objects.get(id=id)
    messages.success(request, "Triggered group update for %s" % user.profile.character.name)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))



@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def user_updategroups_all(request):
    users = spawn_groupupdates()
    messages.success(request, "Triggered updates for %s users" % users)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))



@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def view_user(request, id):
    user = User.objects.get(id=id)
    chars = user.characters.all()

    context = {
        "user": user,
        "discord": user.social_auth.filter(provider="discord").first(),
        "forum_address": settings.FORUM_ADDRESS,
        "kills_last_30": Kill.objects.filter(
                killers__in=chars,
                date__gte=timezone.now() - timedelta(days=30)
            ).distinct().count(),
        "kills_last_90": Kill.objects.filter(
                killers__in=chars,
                date__gte=timezone.now() - timedelta(days=90)
            ).distinct().count(),
    }

    return render(request, "eveauth/user_view.html", context)


@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def unlink_discord(request, id):
    user = User.objects.get(id=id)
    discord = user.social_auth.get(provider="discord")

    if request.method == "POST":
        if request.POST.get("confirm", False) != False:
            # Kick user from discord
            api = DiscordAPI()
            api.kick_member(discord.uid)

            # Delete social auth entry
            discord.delete()

            # Return
            messages.success(request, "Disconnected discord account for user %s" % user.profile.character.name)
            return redirect(view_user, user.id)

    context = {
        'user': user,
        'discord': discord
    }

    return render(request, "eveauth/unlink_discord_confirm.html", context)


@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def adminassets_index(request, user_id):
    user = User.objects.get(id=user_id)

    context = {
        "view_ship": "adminassets_viewship",
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
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def adminassets_viewship(request, id):
    ship = Asset.objects.get(id=id)

    context = {
        "ship": ship,
        "view_ship": "adminassets_viewship"
    }

    return render(request, "eveauth/view_ship.html", context)


@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def groupadmin_index(request):
    groups = Group.objects.exclude(
        Q(name__startswith="Corp: ") | Q(name__startswith="Alliance: ")
    ).order_by(
        'name'
    ).all()

    apps = GroupApp.objects.exclude(
        completed__isnull=False
    ).order_by(
        '-created'
    ).all()

    context = {
        "groups": groups,
        "apps": apps
    }

    return render(request, "eveauth/groupadmin_index.html", context)


@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def groupadmin_create(request):
    group = Group(name="New Group")
    group.save()

    return redirect(groupadmin_edit, group.id)


@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def groupadmin_edit(request, id):
    group = Group.objects.get(id=id)

    # Check if we need to update the group
    if request.POST.get("name", None) != None:
        group.name = request.POST.get("name")
        group.details.is_open = bool(request.POST.get("is_open", False))
        group.details.can_apply = bool(request.POST.get("can_apply", False))
        group.details.mumble = bool(request.POST.get("mumble", False))
        group.details.forum = bool(request.POST.get("forum", False))
        group.details.discord = bool(request.POST.get("discord", False))
        group.save()
        group.details.save()

    context = {
        "group": group,
        "apps": group.apps.filter(accepted=None).order_by('created').all()
    }

    return render(request, "eveauth/groupadmin_edit.html", context)


@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def groupadmin_app_complete(request, app_id, yesno):
    app = GroupApp.objects.get(id=app_id)
    if yesno == "accept":
        app.complete(True, request.user)
        update_discord.delay(app.user.id)
    else:
        app.complete(False, request.user)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def groupadmin_kick(request, group_id, user_id):
    user = User.objects.get(id=user_id)
    group = Group.objects.get(id=group_id)
    group.user_set.remove(user)

    update_discord.delay(user.id)

    messages.success(request, 'Kicked %s from %s' % (user.profile.character.name, group.name))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def groupadmin_delete(request, id):
    group = Group.objects.get(id=id)
    messages.success(request, 'Deleted group %s' % group.name)
    group.delete()
    return redirect(groupadmin_index)


@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def mumbleadmin_index(request):
    server = get_server()

    context = {
        "server": server,
        "users": map(lambda x: x[1], server.getUsers().items())
    }

    o = render(request, "eveauth/mumbleadmin_index.html", context)
    server.ice_getCommunicator().destroy()
    return o



@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def mumbleadmin_kick(request, session_id):
    server = get_server()
    user = server.getUsers()[int(session_id)]
    server.kickUser(int(session_id), "Kicked via web admin")
    messages.success(request, 'Kicked %s from mumble' % user.name)

    server.ice_getCommunicator().destroy()
    return redirect(mumbleadmin_index)


@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def characteradmin_index(request, page=1, order_by=None):
    if order_by == None:
        order_by = "owner"

    order_by_dict = {
        "owner": "owner__username",
        "name": "name",
        "corp": "corp__name",
        "alliance": "alliance__name",
        "ship": "ship__name",
        "ship_type": "ship__group__name",
        "system": "system__name",
        "region": "system__region__name",
    }

    chars = Character.objects.filter(
        owner__isnull=False
    ).prefetch_related(
        'corp',
        'alliance',
        'system',
        'system__region',
    ).order_by(
        order_by_dict[order_by],
        "system__name",
        "name"
    ).all()
    paginator = Paginator(chars, 40)

    context = {
        "characters": paginator.page(page),
        "order_by": order_by
    }

    return render(request, "eveauth/characteradmin_index.html", context)


@login_required
@user_passes_test(lambda x: x.groups.filter(name="admin").exists())
def characteradmin_view(request, id):
    char = Character.objects.prefetch_related(
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
        ).get(id=id)

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

    context = {
        "character": char,
        "skill_groups": skills
    }

    return render(request, "eveauth/character_view.html", context)
