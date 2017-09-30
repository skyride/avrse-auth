from django.utils.timezone import now, timedelta

from django.contrib.auth.models import User, Group
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Corporation(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64)
    ticker = models.CharField(max_length=5)
    group = models.ForeignKey(Group, null=True)
    last_updated = models.DateTimeField(auto_now=True)


    @staticmethod
    def get_or_create(corporation_id):
        from eveauth.esi import ESI

        corporation = Corporation.objects.filter(id=corporation_id)
        if len(corporation) == 0:
            api = ESI()
            corporation = api.get("/corporations/%s/" % corporation_id)
            db_corporation = Corporation(
                id=corporation_id,
                name=corporation['corporation_name'],
                ticker=corporation['ticker']
                )

            # Make Django Group
            group = Group(name="Corp: %s" % db_corporation.name)
            group.save()
            db_corporation.group = group
            db_corporation.save()

            return db_corporation
        else:
            db_corporation = corporation[0]
            if db_corporation.last_updated < now() - timedelta(days=2):
                old_name = db_corporation.name
                api = ESI()
                corporation = api.get("/corporations/%s/" % corporation_id)
                db_corporation.name = corporation['corporation_name']
                db_corporation.ticker = corporation['ticker']
                db_corporation.save()

                # Update group
                db_corporation.group.name = "Corp: %s" % db_corporation.name
                db_corporation.group.save()
            return db_corporation
