from django.db import models
from django_unixdatetimefield import UnixDateTimeField

from murmurserver import MurmurServer


class MurmurLog(models.Model):
    server = models.ForeignKey(MurmurServer, related_name="logs")
    msg = models.TextField()
    msgtime = UnixDateTimeField()


    class Meta:
        unique_together = ("msg", "msgtime")
        db_table = "murmur_slog"
        managed = False
        ordering = ["-msgtime"]
