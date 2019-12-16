import requests
import urllib3
import logging


class HTTPClient():

    def __init__(self, disable_ssl_verify=False, timeout=60):
        self.client = requests.session()
        self.disable_ssl_verify = disable_ssl_verify
        self.timeout = timeout
        self.logger = logging.getLogger()

        if self.disable_ssl_verify:
            print('Disable the insecure request warning.')
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def Get(self, url, headers=None, data=None, json=None, params=None, *args, **kwargs):

        if headers is None:
            headers = {}
        self.logger.debug(f'GET url: {url} headers: {headers} data: {data} json: {json}'
                          f' params: {params}')
        if self.disable_ssl_verify:
            response = self.client.get(url, headers=headers, data=data, json=json, params=params
                                       , verify=False, timeout=self.timeout, *args, **kwargs)
        else:
            response = self.client.get(url, headers=headers, data=data, json=json, params=params
                                       , timeout=self.timeout, *args, **kwargs)
        self.logger.debug(f'Response code: {response.status_code}')
        self.logger.debug(f'Response message: {response.text}')
        return response

    def Post(self, url, headers=None, data=None, json=None, params=None, *args, **kwargs):

        if headers is None:
            headers = {}
        # headers['X-Correlation-Id'] = _generate_correlation_id()
        self.logger.debug(f'POST url: {url} headers: {headers} data: {data} json: {json}'
                          f' params: {params}')
        if self.disable_ssl_verify:
            response = self.client.post(url=url, headers=headers, data=data, json=json
                                        , params=params, verify=False, timeout=self.timeout
                                        , *args, **kwargs)
        else:
            response = self.client.post(url=url, headers=headers, data=data, json=json
                                        , params=params, timeout=self.timeout, *args, **kwargs)
        self.logger.debug(f'Response {response.status_code}:{response.text}')
        return response
