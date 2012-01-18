import urllib
import cgi
import json
import base64
from functools import partial

import pytest
import requests

from tests.helpers import build_authorize_url, build_access_token_url, TEST_SERVER_HOST

# custom asserts

def assert_required_argument(url, argument, method='GET', headers=None):
    error_description = 'Parameter {0} is required'.format(argument)
    assert_invalid_request(url, error_description, method, headers)


def assert_argument_value(url, argument, value, method='GET', headers=None):
    error_description = 'Parameter {0} should be {1}'.format(argument, value)
    assert_invalid_request(url, error_description, method, headers)


def assert_required_header(url, header, method='GET', headers=None):
    error_description = 'Header {0} is required'.format(header)
    assert_invalid_request(url, error_description, method, headers)


def assert_header_value(url, header, value, method='GET', headers=None):
    error_description = 'Header {0} should be {1}'.format(header, value)
    assert_invalid_request(url, error_description, method, headers)


def assert_header_starts_with(url, header, startswith, method='GET', headers=None):
    error_description = 'Header {0} should start with "{1}"'.format(header, startswith)
    assert_invalid_request(url, error_description, method, headers)


def assert_invalid_request(url, error_description, method, headers):
    assert_error_response(url, 'invalid_request', error_description, method, headers)


def assert_invalid_grant(url, error_description, method, headers):
    assert_error_response(url, 'invalid_grant', error_description, method, headers)


def assert_error_response(url, error_code, error_description, method, headers):
    resp = requests.request(method, url, headers=headers)
    assert 'application/json; charset=UTF-8' == resp.headers['content-type']

    body = json.loads(resp.content)
    assert error_code == body['error']
    assert error_description == body['error_description']
    assert 400 == resp.status_code


# helpers

def request_authorization_code(client_id='123',
                               redirect_uri='http://callback'):
    url = build_authorize_url({'client_id': client_id,
                               'response_type': 'code',
                               'redirect_uri': redirect_uri})
    resp = requests.get(url, allow_redirects=False)
    assert 302 == resp.status_code
    code = get_code_from_url(resp.headers['Location'])
    return code

def get_code_from_url(url):
    query = dict(cgi.parse_qsl(url.split('?')[1]))
    return query['code']

def build_basic_authorization_header(client_id, code):
    digest = base64.b64encode('{0}:{1}'.format(client_id, code))
    return 'Basic {0}'.format(digest)

def parse_json_response(response):
    assert 'application/json; charset=UTF-8' == response.headers['content-type']
    return json.loads(response.content)


#
# test authorization request
#

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
    assert 'http://callback?code=am3jah7dl' == resp.headers['Location']


#
# test access token request
#

headers = {
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'Authorization': 'Basic MTIzOmZvbw==',
    }

# validates required headers

def test_should_require_content_type_header():
    assert_required_header(build_access_token_url(), 'content-type', 'POST')


def test_should_require_content_type_header_to_be_x_wwww_form_urlencoded():
    url = build_access_token_url()
    invalid_headers = {'Content-Type': 'text/plain'}

    assert_header_value(build_access_token_url(),
                        'content-type',
                        'application/x-www-form-urlencoded;charset=UTF-8',
                        'POST',
                        invalid_headers)


def test_should_require_authorization_header():
    invalid_headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}
    assert_required_header(build_access_token_url(), 'authorization',
                           'POST',
                           headers=invalid_headers)


def test_authorization_header_should_be_basic():
    invalid_headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                       'Authorization': 'Invalid Basic Header'}

    assert_header_starts_with(build_access_token_url(), 'authorization',
                              'Basic ',
                              'POST',
                              headers=invalid_headers)

def test_should_return_400_with_invalid_request_error_if_base64_header_could_not_be_decoded():
    url = build_access_token_url({'grant_type': 'authorization_code',
                                  'code': 'ccc',
                                  'redirect_uri': 'http://callback'})
    valid_headers = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Authorization': 'Basic this-is-not-base-64',
        }
    expected_response = {
        'error': 'invalid_request',
        'error_description': 'Base 64 from Authorization header could not be decoded'
        }
    resp = requests.post(url, headers=valid_headers)

    assert 400 == resp.status_code
    assert expected_response == parse_json_response(resp)

# validates required POST parameters

def test_should_require_grant_type_argument():
    assert_required_argument(build_access_token_url(), 'grant_type', 'POST',
                             headers=headers)


def test_should_require_grant_type_argument_to_be_authorization_code():
    url = build_access_token_url({'grant_type': 'something-else'})
    assert_argument_value(url, 'grant_type', 'authorization_code', 'POST',
                          headers=headers)


def test_should_require_code_argument():
    url = build_access_token_url({'grant_type': 'authorization_code'})
    assert_required_argument(url, 'code', 'POST', headers=headers)


def test_should_require_redirect_uri_argument():
    url = build_access_token_url({'grant_type': 'authorization_code',
                                  'code': 'foo'})
    assert_required_argument(url, 'redirect_uri', 'POST',
                             headers=headers)


@pytest.mark.xfail
def test_should_return_400_if_invalid_body_format():
    # the client could send the correct headers but invalid body format
    assert 0


# happy path!

def test_happy_path_should_return_access_token_if_valid_authorization_code():
    # tokens generation is stubbed in tests/helpers.py
    client_id = 'client1'
    code = request_authorization_code(client_id)

    url = build_access_token_url({'grant_type': 'authorization_code',
                                  'code': code,
                                  'redirect_uri': 'http://callback'})

    valid_headers = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Authorization': build_basic_authorization_header(client_id, code)
        }

    resp = requests.post(url, headers=valid_headers)

    assert 200 == resp.status_code
    assert 'application/json; charset=UTF-8' == resp.headers['content-type']

    body = json.loads(resp.content)
    assert ['access_token', 'expires_in'] == body.keys()
    assert '321-access-token' == body['access_token']


# all possible errors for access token request

def test_should_return_401_with_invalid_client_error_if_invalid_client_id_on_Authorization_header():
    code = request_authorization_code('client-id')
    url = build_access_token_url({'grant_type': 'authorization_code',
                                  'code': code,
                                  'redirect_uri': 'http://callback'})
    valid_headers = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Authorization': build_basic_authorization_header('INCORREECT-CLIENT-ID', code)
        }
    resp = requests.post(url, headers=valid_headers)
    expected_response = {
        'error': 'invalid_client',
        'error_description': 'Invalid client_id or code on Authorization header',
        }

    assert 401 == resp.status_code
    assert expected_response == parse_json_response(resp)
    assert 'Basic realm="OAuth 2.0 Secure Area"' == resp.headers.get('WWW-Authenticate')


def test_should_return_401_with_invalid_client_error_if_invalid_code_on_Authorization_header():
    code = request_authorization_code('client-id')
    url = build_access_token_url({'grant_type': 'authorization_code',
                                  'code': code,
                                  'redirect_uri': 'http://callback'})
    valid_headers = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Authorization': build_basic_authorization_header('client-id', 'INVALIDCODE')
        }
    resp = requests.post(url, headers=valid_headers)
    expected_response = {
        'error': 'invalid_client',
        'error_description': 'Invalid client_id or code on Authorization header',
        }

    assert expected_response == parse_json_response(resp)
    assert 401 == resp.status_code
    assert 'Basic realm="OAuth 2.0 Secure Area"' == resp.headers.get('WWW-Authenticate')


def test_should_return_400_with_invalid_grant_error_if_code_from_body_was_not_found():
    # there is a code for this client and the authorization header is valid, but
    # the code informed on body is not the correct code
    code = request_authorization_code('client-id')
    url = build_access_token_url({'grant_type': 'authorization_code',
                                  'code': 'INVALID-CODE',
                                  'redirect_uri': 'http://callback'})
    valid_headers = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Authorization': build_basic_authorization_header('client-id', code)
        }
    assert_invalid_grant(url, 'Invalid code for this client', 'POST', valid_headers)


def test_should_return_invalid_grant_error_if_redirect_uri_is_invalid():
    # the redirect uri informed on body is not the same informed when the code 
    # was created
    code = request_authorization_code('client-id', redirect_uri='http://example.com')
    url = build_access_token_url({'grant_type': 'authorization_code',
                                  'code': code,
                                  'redirect_uri': 'http://callback'}) # different uri
    valid_headers = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Authorization': build_basic_authorization_header('client-id', code)
        }
    assert_invalid_grant(url, 'redirect_uri does not match', 'POST', valid_headers)


def test_should_return_invalid_grant_if_duplicate_access_token_request_with_same_authorization_grant():
    client_id = 'client1'
    code = request_authorization_code(client_id)

    url = build_access_token_url({'grant_type': 'authorization_code',
                                  'code': code,
                                  'redirect_uri': 'http://callback'})

    valid_headers = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Authorization': build_basic_authorization_header(client_id, code)
        }

    resp = requests.post(url, headers=valid_headers)
    assert 200 == resp.status_code

    assert_invalid_grant(url, 'authorization grant already used', 'POST',
                         valid_headers)
