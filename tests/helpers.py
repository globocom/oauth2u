import sys
import urllib
import cgi
import base64
import json
from functools import partial

import requests

__all__ = ('TEST_SERVER_HOST',
           'build_root_url',
           'build_basic_authorization_header',
           'build_access_token_url',
           'parse_json_response',
           'parse_query_string',
           'get_code_from_url',
           'request_authorization_code')


TEST_SERVER_HOST = 'http://localhost:8888'


def build_url(host, path, query=None):
    query = query or {}
    return u'{0}/{1}?{2}'.format(host.rstrip('/'),
                                 path.lstrip('/'),
                                 urllib.urlencode(query))


build_root_url = partial(build_url, TEST_SERVER_HOST)
build_authorize_url = partial(build_url, TEST_SERVER_HOST, '/authorize')
build_access_token_url = partial(build_url, TEST_SERVER_HOST, '/access-token')


def parse_json_response(response):
    assert 'application/json; charset=UTF-8' == response.headers['content-type']
    return json.loads(response.content)


def parse_query_string(url):
    url, query_string = url.split('?')
    query = dict(cgi.parse_qsl(query_string))
    return url, query


def get_code_from_url(url):
    ''' Given an url returns the 'code' GET parameter '''
    query = dict(cgi.parse_qsl(url.split('?')[1]))
    return query['code']


def request_authorization_code(client_id='123',
                               redirect_uri='http://callback'):
    ''' Performs a GET on the authorization request url, waits for the 
    redirect and return the code provided 
    '''
    url = build_authorize_url({'client_id': client_id,
                               'response_type': 'code',
                               'redirect_uri': redirect_uri})
    resp = requests.get(url, allow_redirects=False)
    assert 302 == resp.status_code
    code = get_code_from_url(resp.headers['Location'])
    return code


def build_basic_authorization_header(client_id, code):
    ''' Build the value for a Basic ``Authorization`` HTTP header '''
    digest = base64.b64encode('{0}:{1}'.format(client_id, code))
    return 'Basic {0}'.format(digest)
