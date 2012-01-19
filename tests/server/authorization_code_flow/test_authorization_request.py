import requests

from tests.helpers import build_authorize_url
from asserts import *

# validate required GET arguments

def test_should_require_response_type_argument():
    assert_required_argument(build_authorize_url(), 'response_type')


def test_should_require_response_type_argument_to_be_code():
    url = build_authorize_url({'response_type': 'invalid'})
    assert_argument_value(url, 'response_type', 'code')


def test_should_require_client_id_argument():
    url = build_authorize_url({'response_type': 'code'})
    assert_required_argument(url, 'client_id')


def test_should_require_redirect_uri_argument():
    # XXX: it should be optional
    url = build_authorize_url({'client_id': '123',
                               'response_type': 'code'})
    assert_required_argument(url, 'redirect_uri')


def test_should_redirect_to_redirect_uri_argument_passing_auth_token():
    # the default behaviour is to redirect, it can be customized using
    # plugins. see usage on oauth2u/tests/server/test_plugins.py and 
    # oauth2u/examples/
    url = build_authorize_url({'client_id': '123',
                               'response_type': 'code',
                               'redirect_uri': 'http://callback'})
    resp = requests.get(url, allow_redirects=False)
    assert 302 == resp.status_code
    assert resp.headers['Location'].startswith('http://callback?code=')


def test_should_keep_get_query_string_from_redirect_uri_when_adding_code_parameter():
    url = build_authorize_url({'client_id': '123',
                         'response_type': 'code',
                         'redirect_uri': 'http://callback?param1=value1'})
    resp = requests.get(url, allow_redirects=False)
    assert 302 == resp.status_code
    assert resp.headers['Location'].startswith('http://callback?param1=value1&code=')


def test_should_generate_tokens_using_generate_authorization_token_function():
    # tokens generation is stubbed in tests/helpers.py
    url = build_authorize_url({'client_id': '123',
                               'response_type': 'code',
                               'redirect_uri': 'http://callback'})
    resp = requests.get(url, allow_redirects=False)
    assert resp.headers['Location'].startswith('http://callback?code=authorization-code-')
