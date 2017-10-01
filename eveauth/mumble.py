import os, sys
import django
sys.path.append("../")
os.environ['DJANGO_SETTINGS_MODULE'] = 'avrseauth.settings'
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.utils import timezone
from django.db.models import Q

from eveauth.models import TemplinkUser

import Ice
Ice.loadSlice( '', ['-I' + Ice.getSliceDir(), "Murmur.ice"])
import Murmur


class ServerAuthenticatorI(Murmur.ServerUpdatingAuthenticator):
    def __init__(self, server, adapter):
      self.server = server

    def authenticate(self, name, pw, certlist, certhash, strong, current=None):
    #   print certhash, strong
    #   for cert in certlist:
    #     cert = X509.load_cert_der_string(cert)
    #     print cert.get_subject(), "issued by", cert.get_issuer()
    #   groups = ("GroupA", "GroupB");
    #   if (name == "One"):
    #     if (pw == "Magic"):
    #       return (1, "One", groups)
    #     else:
    #       return (-1, None, None)
    #   elif (name == "Two"):
    #     if (pw == "Mushroom"):
    #       return (2, "twO", groups)
    #     else:
    #       return (-1, None, None)
    #   elif (name == "White Space"):
    #     if (pw == "Space White"):
    #       return (3, "White Space", groups)
    #     else:
    #       return (-1, None, None)
    #   elif (name == "Fail"):
    #     time.sleep(6)
        if name == "SuperUser":
            return (-2, None, None)

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
            if profile.level >= 0:
                # Test password
                if profile.mumble_password != None:
                    hasher = PBKDF2PasswordHasher()
                    salt = profile.mumble_password.split("$")[2]
                    password = hasher.encode(pw, salt)
                    if password == profile.mumble_password:
                        tag = ""

                        if db_user.groups.filter(name="admin").exists():
                            tag = "[SA]"

                        out_name = "#%s - %s %s" % (
                            profile.corporation.ticker,
                            profile.character.name,
                            tag
                        )

                        groups = db_user.groups.values_list('name', flat=True)

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
      print "getInfo ", id
      name = self.idToName(id);
      if (name == None):
        return (False, {})
      map = {}
      map[Murmur.UserInfo.UserName]=name
      return (True, map)

    def nameToId(self, name, current=None):
      if (name == "One"):
        return 1
      elif (name == "Twoer"):
        return 2
      else:
        return -2;

    def idToName(self, id, current=None):
      if (id == 1):
        return "One"
      elif (id == 2):
        return "Two"
      else:
        return None

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

    map = {};
    map[Murmur.UserInfo.UserName] = 'TestUser';

    # for server in meta.getBootedServers():
    #   ids= server.getUserIds(["TestUser"])
    #   for name,id in ids.iteritems():
    #     if (id > 0):
    #       print "Will unregister ", id
    #       server.unregisterUser(id)
    #   server.registerUser(map)

    print 'Script running (press CTRL-C to abort)';
    try:
        ice.waitForShutdown()
    except KeyboardInterrupt:
        print 'CTRL-C caught, aborting'

    meta.removeCallback(metaR)
    ice.shutdown()
    print "Goodbye"
