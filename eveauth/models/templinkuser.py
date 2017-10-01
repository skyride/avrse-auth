from django.db import models

from templink import Templink

class TemplinkUser(models.Model):
    templink = models.ForeignKey(Templink, related_name="users")
    name = models.CharField(max_length=64, unique=True)
    password = models.CharField(max_length=32, db_index=True)
    created = models.DateTimeField(auto_now=True)


    def mumble_id(self):
        return self.id + 10000000

    def mumble_name(self):
        return "[%s] %s" % (
            self.templink.tag,
            self.name
        )
