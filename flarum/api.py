import requests

from django.core.cache import cache
from django.conf import settings

from flarum.exceptions import FlarumBadUrl, FlarumAuthException, error_code_handler


class FlarumAPI(object):
    token = ""
    user_id = None

    def __init__(self):
        self._check_url()
        self._hydrate_token()

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


    def _check_url(self):
        """Checks if the URL provided has a valid Flarum install"""
        data = cache.get("flarum_check_url:%s" % settings.FLARUM_URL)
        if data == True:
            return
        elif data == False:
            raise FlarumBadUrl("FLARUM_URL does not appear to be a Flarum forum")

        url = self._url("/forum")
        r = requests.get(url)
        if r.status_code != 200:
            raise FlarumBadUrl("Bad URL, couldn't fetch forum information from %s" % url)

        try:
            data = r.json()
            assert data['data']['type'] == "forums"
            cache.set("flarum_check_url:%s" % settings.FLARUM_URL, True, 1200)
        except (ValueError, KeyError, AssertionError):
            cache.set("flarum_check_url:%s" % settings.FLARUM_URL, False, 1200)
            raise FlarumBadUrl("FLARUM_URL does not appear to be a Flarum forum")


    def _hydrate_token(self):
        """Hydrates the object a flarum token from either the Django cache or the Flarum Endpoint"""
        data = cache.get("flarum_token:%s" % settings.FLARUM_URL)

        if data is None:
            r = requests.post(
                self._url("/token"),
                json={
                    "identification": settings.FLARUM_USERNAME,
                    "password": settings.FLARUM_PASSWORD
                }
            )
            data = r.json()

            if r.status_code != 200:
                raise FlarumAuthException("Failed to fetch token")
            cache.set("flarum_token:%s" % settings.FLARUM_URL, data, 1200)

        self.token = data['token']
        self.user_id = data['userId']


    def _call(self, func, url, *args, **kwargs):
        headers = {"Authorization": "Token %s" % self.token}
        kwargs['headers'] = headers

        r = func(self._url(url), *args, **kwargs)
        error_code_handler(r)
        return r


    def _url(self, url):
        return settings.FLARUM_URL + "/api" + url