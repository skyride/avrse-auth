from django.utils.timezone import now, timedelta

from django.contrib.auth.models import User, Group
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Alliance(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64)
    ticker = models.CharField(max_length=5)
    group = models.ForeignKey(Group, null=True)
    last_updated = models.DateTimeField(auto_now=True)


    def __unicode__(self):
        return self.ticker


    @staticmethod
    def get_or_create(alliance_id):
        from eveauth.esi import ESI
        api = ESI()

        db_alliance = Alliance.objects.filter(id=alliance_id)
        if len(db_alliance) == 0:
            alliance = api.get("/alliances/%s/" % alliance_id)
            db_alliance = Alliance(
                id=alliance_id,
                name=alliance['name'],
                ticker=alliance['ticker']
            )

            # Make django group
            group = Group(name="Alliance: %s" % db_alliance.name)
            group.save()
            db_alliance.group = group

            db_alliance.save()

            return db_alliance
        else:
            db_alliance = db_alliance[0]
            if db_alliance.last_updated < now() - timedelta(days=2):
                alliance = api.get("/alliances/%s/" % alliance_id)
                db_alliance.name = alliance['name']
                db_alliance.ticker = alliance['ticker']
                db_alliance.save()

                db_alliance.group.name = "Alliance: %s" % db_alliance.name
                db_alliance.group.save()

            return db_alliance
