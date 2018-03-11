from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, F
from django.db.models.functions import Coalesce
from django.shortcuts import render

from eveauth.models import Corporation


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

    context = {
        "corps": corps
    }

    return render(request, "eveauth/logistics/structures_index.html", context)


@login_required
@user_passes_test(lambda x: x.groups.filter(name__in=["admin", "logistics"]).exists())
def structures_list(request, corp_id, order_by):
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

    return render(request, "eveauth/logistics/structures_list.html", context)