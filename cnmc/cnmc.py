# -*- coding: utf-8 -*-

from authlib.client import OAuth1Session
import logging
from authlib.common.urls import add_params_to_uri       

CNCM_envs = {
    'prod': 'https://api.cnmc.gob.es',
    'staging': 'https://apipre.cnmc.gob.es',
}

class CNMC_API(object):

    def __init__(self, key=None, secret=None, environment=None, **kwargs):
        logging.info("Initializing CNCM Client")

        # Handle the key
        if not key:
            assert 'key' in kwargs
            key = kwargs['key']
        assert type(key) == str, "The key must be an string. Current type '{}'".format(type(key))
        self.key = key

        # Handle the secret
        if not secret:
            assert 'secret' in kwargs
            secret = kwargs['secret']
        assert type(secret) == str, "The key must be an string. Current type '{}'".format(type(secret))
        self.secret = secret

        # Handle environment, default value "prod"
        self.environment = "prod"
        if not environment:
            if 'environment' in kwargs:
                assert type(kwargs['environment']) == str, "environment argument must be an string"
                assert kwargs['environment'] in CNCM_envs.keys(), "Provided environment '{}' not recognized in defined CNMC_envs {}".format(kwargs['environment'], str(FACE_ENVS.keys()))
                self.environment = kwargs['environment']

        self.url = CNCM_envs[self.environment]

        self.session = OAuth1Session(self.key, self.secret, signature_method="HMAC-SHA1", signature_type="HEADER")

    @property
    def NIF(self):
        return "XXXXX"

    def set_request_token (self):
        """
        Set the request token for current session
        """
        self.request_token = self.session.fetch_request_token(self.url)


    def method(self, method, resource, **kwargs):
        """
        Main method handler

        Fetch the requested URL with the requested action through the OAuth session and return a JSON representeation of the response with the resultant code
        """
        url = self.url + resource
        response = self.session.request(method=method, url=url, **kwargs)

        # Handle errors        
        if response.status_code >= 400:
            return {
                'code': response.status_code,
                'error': True,
                'message': str(response),
            }
        else:
            return {
                'code': response.status_code,
                'result': response.json(),
                'error': False,
            }


    def get(self, resource, **kwargs):
        """
        GET method, it dispatch a session.get method consuming the desired resource
        """
        return self.method(method="GET", resource=resource, **kwargs)


    def post(self, resource, **kwargs):
        """
        POST method, it dispatch a session.get method consuming the desired resource
        """
        return self.method(method="POST", resource=resource, **kwargs)
