from datetime import datetime, timedelta

from django.db import models


class Character(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64)
    last_updated = models.DateTimeField(auto_now=True)


    @staticmethod
    def get_or_create(id):
        from eveauth.esi import ESI

        db_char = Character.objects.filter(id=id)
        if len(db_char) == 0:
            api = ESI()
            char = api.get("/characters/%s/" % id)
            db_char = Character(
                id=id,
                name=char['name']
            )
            db_char.save()
        else:
            db_char = db_char[0]

        return db_char
