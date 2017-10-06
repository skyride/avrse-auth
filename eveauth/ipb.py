import requests

from django.conf import settings
from django.utils.crypto import get_random_string


# IPBoard Micro API
class IPBUser:
    def __init__(self, user):
        self.user = user
        if user.profile.forum_id:
            self.member = self._get_member(user.profile.forum_id)
        else:
            self.member = self._create_member()


    # Update access level
    def update_access_level(self):
        data = {
            "group": settings.FORUM_ACCESS_GROUPS[self.user.profile.level]
        }
        r = self._request(requests.post, "/core/members/%s" % self.user.profile.forum_id, data=data)
        self.member = r.json()


    def update_password(self, password):
        data = {
            "password": password
        }
        r = self._request(requests.post, "/core/members/%s" % self.user.profile.forum_id, data=data)
        self.member = r.json()


    def _get_all_groups(self):
        # Get first page
        r = self._request(requests.get, "/core/groups").json()
        groups = r['results']
        for i in range(1, r['totalPages']):
            groups.extend(self._request(requests.get, "/core/groups").json()['results'])
        return groups


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
            "password": get_random_string(32),
            "group": settings.FORUM_ACCESS_GROUPS[self.user.profile.level]

        }
        r = self._request(requests.post, "/core/members", data=data)
        member = r.json()

        self.user.profile.forum_id = member['id']
        self.user.profile.save()

        return member


    def _request(self, method, uri, data=None, params={}):
        params.update({'key': settings.FORUM_API_KEY})
        return method("%sapi/index.php?%s" % (settings.FORUM_ADDRESS, uri), params=params, data=data)
