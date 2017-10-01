from django.db import models
from django.contrib.auth.models import User
from django_unixdatetimefield import UnixDateTimeField

from murmurserver import MurmurServer
from murmurchannel import MurmurChannel


class MurmurUser(models.Model):
    server = models.ForeignKey(MurmurServer, related_name="users")
    user_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    pw = models.CharField(max_length=128)
    lastchannel = models.ForeignKey(MurmurChannel, db_column="lastchannel")
    texture = models.BinaryField()
    last_active = UnixDateTimeField()


    class Meta:
        db_table = "murmur_users"
        managed = False
