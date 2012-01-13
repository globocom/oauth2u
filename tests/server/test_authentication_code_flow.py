import urllib
from functools import partial

import requests
# from tests.helpers import build_url

TEST_SERVER_HOST = 'http://localhost:8888'


def build_url(host, path, query=None):
    query = query or {}
    return u'{0}/{1}?{2}'.format(host.rstrip('/'),
                                 path.lstrip('/'),
                                 urllib.urlencode(query))

authorize_url = partial(build_url, TEST_SERVER_HOST, '/authorize')


def test_should_require_response_type_argument():
    resp = requests.get(authorize_url())
    assert 400 == resp.status_code
    assert 'Missing argument response_type' in resp.content


def test_should_require_client_id_argument():
    resp = requests.get(authorize_url({'response_type': 'code'}))
    assert 400 == resp.status_code
    assert 'Missing argument client_id' in resp.content


def test_should_only_allow_response_type_to_be_code():
    resp = requests.get(authorize_url({'response_type': 'FOO'}))
    assert 400 == resp.status_code
    assert 'response_type should be code' in resp.content


def test_should_require_redirect_uri_argument():
    # XXX: it should be optional
    resp = requests.get(authorize_url({'client_id': '123',
                                       'response_type': 'code'}))
    assert 400 == resp.status_code
    assert 'Missing argument redirect_uri' in resp.content


def test_should_redirect_to_redirect_uri_argument_passing_auth_token():
    url = authorize_url({'client_id': '123',
                         'response_type': 'code',
                         'redirect_uri': 'http://callback'})
    resp = requests.get(url, allow_redirects=False)
    assert 302 == resp.status_code
    assert resp.headers['Location'].startswith('http://callback?code=')


def test_should_keep_get_query_string_from_redirect_uri_when_adding_code_parameter():
    url = authorize_url({'client_id': '123',
                         'response_type': 'code',
                         'redirect_uri': 'http://callback?param1=value1'})
    resp = requests.get(url, allow_redirects=False)
    assert 302 == resp.status_code
    assert resp.headers['Location'].startswith('http://callback?param1=value1&code=')


def test_should_generate_tokens_using_generate_authorization_token_function():
    # tokens generation is stubbed in tests/helpers.py
    url = authorize_url({'client_id': '123',
                         'response_type': 'code',
                         'redirect_uri': 'http://callback'})
    resp = requests.get(url, allow_redirects=False)
    assert 'http://callback?code=123-abc' == resp.headers['Location']
