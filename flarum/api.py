import requests

from django.core.cache import cache
from django.conf import settings


class FlarumAuthException(Exception):
    """Raised when any error occurs relating to lack of permissions"""


class FlarumAPI(object):
    def __init__(self):
        r = requests.post(
            self._url("/token"),
            json={
                "identification": settings.FLARUM_USERNAME,
                "password": settings.FLARUM_PASSWORD
            }
        )

        if r.status_code != 200:
            raise FlarumAuthException("Failed to fetch token")

        data = r.json()
        self.token = data['token']
        self.user_id = data['userId']


    def get(self, url, *args, **kwargs):
        return self._call(requests.get, url, *args, **kwargs)

    def post(self, url, *args, **kwargs):
        return self._call(requests.post, url, *args, **kwargs)

    def put(self, url, *args, **kwargs):
        return self._call(requests.put, url, *args, **kwargs)

    def patch(self, url, *args, **kwargs):
        return self._call(requests.patch, url, *args, **kwargs)

    def delete(self, url, *args, **kwargs):
        return self._call(requests.delete, url, *args, **kwargs)    


    def _call(self, func, url, *args, **kwargs):
        headers = {"Authorization": "Token %s" % self.token}
        kwargs['headers'] = headers
        return func(self._url(url), *args, **kwargs)


    def _url(self, url):
        return settings.FLARUM_URL + "/api" + url