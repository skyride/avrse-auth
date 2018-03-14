from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, F
from django.db.models.functions import Coalesce
from django.http import HttpResponseRedirect
from django.shortcuts import render

from eveauth.models import Corporation, Structure
from sde.models import System


@login_required
@user_passes_test(lambda x: x.groups.filter(name__in=["admin", "logistics"]).exists())
def structures_index(request):
    corps = []
    for corp in Corporation.objects.annotate(
        structure_count=Count('structures'),
    ).filter(
        structure_count__gt=0,
    ).order_by(
        '-structure_count',
        'name'
    ).all():
        if corp.characters.filter(
            roles__name="Director",
            token__isnull=False
        ).exists():
            corps.append(corp)

    systems = []
    for system in System.objects.annotate(
        structure_count=Count('structures'),
    ).filter(
        structure_count__gt=0,
    ).order_by(
        '-structure_count',
        'region__name',
        'name'
    ).all():
        systems.append(system)

    context = {
        "systems": systems,
        "corps": corps
    }

    return render(request, "eveauth/logistics/structures_index.html", context)


@login_required
@user_passes_test(lambda x: x.groups.filter(name__in=["admin", "logistics"]).exists())
def structures_list_corp(request, corp_id, order_by):
    corp = Corporation.objects.get(id=corp_id)

    order_by = {
        "": "system__region__name",
        "fuel": F("timer").asc(nulls_last=True),
        "type": 'type__name',
        "services": '-service_count',
        "name": 'station__name',
        "state": 'state'
    }[order_by]

    context = {
        "corp": corp,
        "structures_list": "structures_list_corp",
        "structures": corp.structures.annotate(
                service_count=Count('services'),
                timer=Coalesce('state_timer_end', 'fuel_expires')
            ).prefetch_related(
                'system',
                'system__region',
                'type',
                'station'
            ).order_by(
                order_by,
                'system__region__name',
                'system__name',
                F("timer").asc(nulls_last=True),
                '-type__mass',
                'station__name'
            )
    }

    return render(request, "eveauth/logistics/structures_list_corp.html", context)


@login_required
@user_passes_test(lambda x: x.groups.filter(name__in=["admin", "logistics"]).exists())
def structures_list_system(request, system_id, order_by):
    system = System.objects.get(id=system_id)

    order_by = {
        "": "system__region__name",
        "fuel": F("timer").asc(nulls_last=True),
        "type": 'type__name',
        "services": '-service_count',
        "name": 'station__name',
        "state": 'state'
    }[order_by]

    context = {
        "system": system,
        "structures_list": "structures_list_system",
        "structures": system.structures.annotate(
                service_count=Count('services'),
                timer=Coalesce('state_timer_end', 'fuel_expires')
            ).prefetch_related(
                'system',
                'system__region',
                'type',
                'station'
            ).order_by(
                order_by,
                F("timer").asc(nulls_last=True),
                '-type__mass',
                'station__name'
            )
    }

    return render(request, "eveauth/logistics/structures_list_system.html", context)


@login_required
@user_passes_test(lambda x: x.groups.filter(name__in=["admin", "logistics"]).exists())
def structures_fuelnotification_toggle(request, structure_id, state):
    structure = Structure.objects.get(id=structure_id)

    if state == "on":
        structure.fuel_notifications = True
        structure.save()
    elif state == "off":
        structure.fuel_notifications = False
        structure.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))