import requests
import socket
import json
import datetime
import pytz

from base64 import b64encode
from urllib import urlencode
from hashlib import sha256

from django.core.cache import cache
from django.conf import settings


def parse_api_date(date):
    date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
    return pytz.utc.localize(date)

# ESI Api wrapper
class ESI():
    url = settings.ESI_URL
    datasource = settings.ESI_DATASOURCE
    client_id = settings.SOCIAL_AUTH_CHARACTER_AUTH_KEY
    secret_key = settings.SOCIAL_AUTH_CHARACTER_AUTH_SECRET

    cache_time = 30
    token = None
    fleet_id = None


    # Wrapper for GET
    def get(self, url, data=None, get_vars={}, cache_time=None, debug=settings.DEBUG):
        if cache_time == None:
            cache_time = self.cache_time
        return self.request(url, data=data, method=requests.get, get_vars=get_vars, cache_time=cache_time, debug=debug)

    # Wrapper for POST
    def post(self, url, data=None, get_vars={}, cache_time=None, debug=settings.DEBUG):
        if cache_time == None:
            cache_time = self.cache_time
        return self.request(url, data=data, method=requests.post, get_vars=get_vars, cache_time=cache_time, debug=debug)

    def put(self, url, data=None, get_vars={}, cache_time=None, debug=settings.DEBUG):
        if cache_time == None:
            cache_time = self.cache_time
        return self.request(url, data=data, method=requests.put, get_vars=get_vars, cache_time=cache_time, debug=debug)

    def delete(self, url, data=None, get_vars={}, cache_time=None, debug=settings.DEBUG):
        if cache_time == None:
            cache_time = self.cache_time
        return self.request(url, data=data, method=requests.delete, get_vars=get_vars, cache_time=cache_time, debug=debug)


    def request(self, url, data=None, method=requests.get, retries=0, get_vars={}, cache_time=None, debug=settings.DEBUG):
        if cache_time == None:
            cache_time = self.cache_time

        # Do replacements
        full_url = self._replacements(url)

        # Try request
        full_url = "%s%s?%s" % (self.url, full_url, self._get_variables(get_vars))
        if debug:
            print full_url

        # Check the cache for a response
        if self.token == None:
            cache_key = sha256("%s:%s:%s" % (str(method), full_url, json.dumps(data))).hexdigest()
        else:
            cache_key = sha256("%s:%s:%s:%s" % (str(method), self.token.extra_data['access_token'], full_url, json.dumps(data))).hexdigest()

        if cache_time > 0:
            r = cache.get(cache_key)
            if r != None:
                r = json.loads(r)
                if r == None:
                    self.log(url=url, full_url=full_url, method=method, get_vars=get_vars, cache_hit=True, success=True)
                    return None
                else:
                    self.log(url=url, full_url=full_url, method=method, get_vars=get_vars, cache_hit=True, success=False)
                    return r

        # Nope, no cache, hit the API
        r = method(full_url, data=data, headers=self._bearer_header())

        # If we got a 403 error its an invalid token, try to refresh the token and try again
        if r.status_code == 403:
            if self._refresh_access_token():
                r = method(full_url, data=data, headers=self._bearer_header())
                # If the status code is still 403 then we fail the request
                if r.status_code == 403:
                    cache.set(cache_key, json.dumps(None), cache_time)
                    self.log(url=url, full_url=full_url, method=method.__name__, get_vars=get_vars, cache_hit=False, status_code=403, success=False)
                    return None
            else:
                self.log(url=url, full_url=full_url, method=method.__name__, get_vars=get_vars, cache_hit=False, status_code=403, success=False)
                return None

        # ESI is buggy, so lets give it up to 10 retries for 500 error
        if r.status_code in [500, 502]:
            if retries < settings.ESI_RETRIES:
                return self.request(url, data=data, method=method, retries=retries+1)
            else:
                cache.set(cache_key, json.dumps(None), cache_time)
                self.log(url=url, full_url=full_url, method=method.__name__, get_vars=get_vars, cache_hit=False, status_code=r.status_code, success=False)
                return None

        # Load json and return
        if r.status_code == 200:
            j = json.loads(r.text)
            cache.set(cache_key, r.text, cache_time)
            self.log(url=url, full_url=full_url, method=method.__name__, get_vars=get_vars, cache_hit=False, status_code=r.status_code, success=True)
            return j
        else:
            cache.set(cache_key, json.dumps(None), cache_time)
            self.log(url=url, full_url=full_url, method=method.__name__, get_vars=get_vars, cache_hit=False, status_code=r.status_code, success=False)
            return None


    # Takes an ESIToken object as the constructor
    def __init__(self, token=None, fleet_id=None):
        self.token = token
        self.fleet_id = fleet_id


    # Replaces url $variables with their values
    def _replacements(self, url):
        if self.token != None:
            url = url.replace("$id", str(self.token.extra_data['id']))
        if self.fleet_id != None:
            url = url.replace("$fleet", str(self.fleet_id))

        return url


    def _bearer_header(self):
        if self.token == None:
            headers = {}
        else:
            headers = {
                "Authorization": "Bearer %s" % self.token.extra_data['access_token']
            }
        return headers


    def _get_variables(self, get_vars):
        get_vars['datasource'] = self.datasource
        return urlencode(get_vars)


    # Refreshes the access token using the refresh token
    def _refresh_access_token(self):
        # Get the new access token
        auth = b64encode("%s:%s" % (self.client_id, self.secret_key))
        headers = {
            "Authorization": "Basic %s" % auth
        }
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.token.extra_data['refresh_token']
        }
        r = requests.post("https://login.eveonline.com/oauth/token", data=data, headers=headers)

        # If we get a 400 code, then the key has been deleted
        if r.status_code == 400:
            self.log(type='esi_token_refresh', success=False)
            return False

        # Update the ESI token
        r = json.loads(r.text)
        self.token.extra_data['access_token'] = r['access_token']
        self.token.save()

	self.log(type='esi_token_refresh', success=True)
        return True


    def log(self, **kwargs):
        data = {'type': 'esi_call'}
        if self.token != None:
            data.update({'token_id': self.token.id, 'token_uid': self.token.uid})
        else:
            data.update({'token_id': None})
        data.update(kwargs)
        self._send_log(data)


    def _send_log(self, data):
        if getattr(settings, 'LOGSTASH_HOST', False) != False:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((settings.LOGSTASH_HOST, settings.LOGSTASH_PORT))
            sock.sendall(json.dumps(data) + "\n")
            sock.close()
