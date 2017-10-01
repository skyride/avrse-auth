from django.db import models


class MurmurServer(models.Model):
    server_id = models.IntegerField(primary_key=True)

    class Meta:
        db_table = "murmur_servers"
        managed = False
