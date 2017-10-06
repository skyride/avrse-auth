import requests

from django.conf import settings
from django.utils.crypto import get_random_string


# IPBoard Micro API
class IPB:
    def __init__(self, user):
        self.user = user
        if user.profile.forum_id:
            self.member = self._get_member(user.profile.forum_id)
        else:
            self.member = self._create_member()


    def update_password(self, password):
        data = {
            "password": password
        }
        r = self._request(requests.post, "/core/members/%s" % self.user.profile.forum_id, data=data)
        self.member = r.json()


    def _get_member(self, id):
        r = self._request(requests.get, "/core/members/%s" % id)
        if r.status_code == 200:
            return r.json()
        else:
            return None


    def _create_member(self):
        data = {
            "name": self.user.profile.character.name,
            "email": "%s@avrse.men" % self.user.username,
            "password": get_random_string(32)
        }
        r = self._request(requests.post, "/core/members", data=data)
        member = r.json()

        self.user.profile.forum_id = member['id']
        self.user.profile.save()

        return member


    def _request(self, method, uri, data=None):
        return method("%sapi/index.php?%s" % (settings.FORUM_ADDRESS, uri), params={'key': settings.FORUM_API_KEY}, data=data)
