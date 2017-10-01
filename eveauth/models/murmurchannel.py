from django.db import models

from murmurserver import MurmurServer


class MurmurChannel(models.Model):
    server = models.ForeignKey(MurmurServer, related_name="channels")
    channel_id = models.IntegerField(primary_key=True)
    parent = models.ForeignKey("self", null=True, related_name="subchannels")
    name = models.CharField(max_length=255)
    inheritacl = models.IntegerField(null=True)


    class Meta:
        db_table = "murmur_channels"
        managed = False
