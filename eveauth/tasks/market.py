import requests

from django.db import transaction

from avrseauth.celery import app
from sde.models import Type


@app.task(name="spawn_price_updates")
def spawn_price_updates(inline=False):
    def chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    id_chunks = chunks(
        list(
            Type.objects.filter(
                published=True,
                market_group__isnull=False
            ).values_list(
                'id',
                flat=True
            )
        ),
        500
    )

    for chunk in id_chunks:
        if inline:
            update_prices(chunk)
        else:
            update_prices.delay(chunk)
    print "Queued price updates"


@app.task(name="update_prices")
def update_prices(item_ids):
    r = requests.get(
        "https://market.fuzzwork.co.uk/aggregates/",
        params={
            "region": 10000002,
            "types": ",".join(map(str, item_ids))
        }
    ).json()

    with transaction.atomic():
        for key in r.keys():
            item = r[key]
            db_type = Type.objects.get(id=int(key))
            db_type.buy = item['buy']['percentile']
            db_type.sell = item['sell']['percentile']
            db_type.save()

    print "Price updates completed for %s:%s" % (
        item_ids[0],
        item_ids[-1]
    )