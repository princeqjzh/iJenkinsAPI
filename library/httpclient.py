import requests
import urllib3


class HTTPClient():

    def __init__(self, disable_ssl_verify=False, timeout=60):
        self.client = requests.session()
        self.disable_ssl_verify = disable_ssl_verify
        self.timeout = timeout

        if self.disable_ssl_verify:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def Get(self, url, headers=None, data=None, json=None, params=None, *args, **kwargs):

        if headers is None:
            headers = {}

        if self.disable_ssl_verify:
            response = self.client.get(url, headers=headers, data=data, json=json, params=params
                                       , verify=False, timeout=self.timeout, *args, **kwargs)
        else:
            response = self.client.get(url, headers=headers, data=data, json=json, params=params
                                       , timeout=self.timeout, *args, **kwargs)
        return response

    def Post(self, url, headers=None, data=None, json=None, params=None, *args, **kwargs):

        if headers is None:
            headers = {}

        if self.disable_ssl_verify:
            response = self.client.post(url=url, headers=headers, data=data, json=json
                                        , params=params, verify=False, timeout=self.timeout
                                        , *args, **kwargs)
        else:
            response = self.client.post(url=url, headers=headers, data=data, json=json
                                        , params=params, timeout=self.timeout, *args, **kwargs)
        return response
