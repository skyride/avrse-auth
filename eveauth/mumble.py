import os, sys
import django
sys.path.append("../")
os.environ['DJANGO_SETTINGS_MODULE'] = 'avrseauth.settings'
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.utils import timezone
from django.db.models import Q
from django.conf import settings

from eveauth.models import TemplinkUser

import Ice
Ice.loadSlice( '', ['-I' + Ice.getSliceDir(), "Murmur.ice"])
import Murmur


class ServerAuthenticatorI(Murmur.ServerUpdatingAuthenticator):
    def __init__(self, server, adapter):
      self.server = server

    def authenticate(self, name, pw, certlist, certhash, strong, current=None):
        # Superuser fallback
        if name == "SuperUser":
            return (-2, None, None)

        # Search for user
        db_user = User.objects.filter(
            username=name
        ).prefetch_related(
            "groups",
            "profile",
            "profile__corporation",
            "profile__character"
        )
        if db_user.count() > 0:
            db_user = db_user[0]
            profile = db_user.profile

            # Test access level
            if profile.level >= settings.MUMBLE_ACCESS_LEVEL:
                # Test password
                if profile.mumble_password != None:
                    hasher = PBKDF2PasswordHasher()
                    salt = profile.mumble_password.split("$")[2]
                    password = hasher.encode(pw, salt)
                    if password == profile.mumble_password:
                        # Name
                        out_name = "#%s - %s" % (
                            profile.corporation.ticker,
                            profile.character.name
                        )

                        # Groups
                        groups = list(db_user.groups.values_list('name', flat=True))
                        groups.append(["Non-members", "Blues", "Members"][profile.level])

                        # Register a login
                        db_user.last_login = timezone.now()
                        db_user.save()

                        return (db_user.id, out_name, groups)

        # Check if the password is a templink key
        if name == "templink":
            templink_user = TemplinkUser.objects.filter(
                Q(templink__expires__gte=timezone.now()) | Q(templink__expires__isnull=True),
                templink__active=True,
                password=pw
            )
            if templink_user.exists():
                templink_user = templink_user.first()
                groups = [
                    "templink",
                    "templink_%s" % templink_user.templink.id
                ]
                return (templink_user.mumble_id(), templink_user.mumble_name(), groups)

        return (-1, None, None)


    def getInfo(self, id, current=None):
      print "User Connected: %s" % (id)
      name = self.idToName(id);
      if (name == -2):
        return (False, {})
      map = {}
      map[Murmur.UserInfo.UserName]=name
      return (True, map)


    def nameToId(self, name, current=None):
        return -2;


    def idToName(self, id, current=None):
        return None;


    def idToTexture(self, id, current=None):
        return None

    # The expanded methods from UpdatingAuthenticator. We only implement a subset for this example, but
    # a valid implementation has to define all of them
    def registerUser(self, name, current=None):
      print "Someone tried to register " + name[Murmur.UserInfo.UserName]
      return -2


    def unregisterUser(self, id, current=None):
      print "Unregister ", id
      return -2


    def getRegistration(self, id, current=None):
      return (-2, None, None)


    def setInfo(self, id, info, current=None):
      print "Set", id, info
      return -1


if __name__ == "__main__":
    global contextR

    print "Creating callbacks...",
    ice = Ice.initialize(sys.argv)

    meta = Murmur.MetaPrx.checkedCast(ice.stringToProxy('Meta:tcp -h 127.0.0.1 -p 6502'))
    adapter = ice.createObjectAdapterWithEndpoints("Callback.Client", "tcp -h 127.0.0.1")
    adapter.activate()

    for server in meta.getBootedServers():
      serverR=Murmur.ServerUpdatingAuthenticatorPrx.uncheckedCast(adapter.addWithUUID(ServerAuthenticatorI(server, adapter)))
      server.setAuthenticator(serverR)

    print "Done"
    print 'Script running (press CTRL-C to abort)';
    try:
        ice.waitForShutdown()
    except KeyboardInterrupt:
        print 'CTRL-C caught, aborting'

    #meta.removeCallback(metaR)
    ice.shutdown()
    ice.destroy()
    print "Goodbye"
