import requests
import pytest

from tests.helpers import (build_access_token_url, parse_json_response,
                           request_authorization_code, build_basic_authorization_header)
from asserts import *

headers = {
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'Authorization': 'Basic MTIzOmZvbw==',
    }

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
    body = parse_json_response(resp)

    assert 200 == resp.status_code
    assert ['access_token', 'token_type', 'expires_in'] == body.keys()
    assert body['access_token'].startswith('access-token-')
    assert 'bearer' == body['token_type']



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
    code = request_authorization_code('client-id')
    url = build_access_token_url({'grant_type': 'authorization_code',
                                  'code': code,
                                  'redirect_uri': 'http://callback'})
    valid_headers = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Authorization': build_basic_authorization_header('client-id', code)
        }

    resp = requests.post(url, headers=valid_headers)
    assert 200 == resp.status_code
    # performs a new POST to get the access token, but it has already been taken
    assert_invalid_grant(url, 'Authorization grant already used', 'POST',
                         valid_headers)



# multiple users authenticating

def test_multiple_users_should_be_able_to_authenticate():
    yield ("using same client id",
           check_multiple_users_with_client_ids, 'client-id', 'client-id')
    yield ("using different client ids",
           check_multiple_users_with_client_ids, 'bob-client-id', 'ted-client-id')

def check_multiple_users_with_client_ids(bob_client_id, ted_client_id):
    bob_code = request_authorization_code(bob_client_id)
    ted_code = request_authorization_code(ted_client_id)

    bob_url = build_access_token_url({'grant_type': 'authorization_code',
                                      'code': bob_code,
                                      'redirect_uri': 'http://callback'})
    ted_url = build_access_token_url({'grant_type': 'authorization_code',
                                      'code': ted_code,
                                      'redirect_uri': 'http://callback'})

    bob_response = requests.post(bob_url, headers={
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'Authorization': build_basic_authorization_header(bob_client_id, bob_code)
            })
    ted_response = requests.post(ted_url, headers={
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'Authorization': build_basic_authorization_header(ted_client_id, ted_code)
            })

    assert 200 == bob_response.status_code
    assert 200 == ted_response.status_code

    bob_json = parse_json_response(bob_response)
    ted_json = parse_json_response(ted_response)

    assert ['access_token', 'token_type', 'expires_in'] == bob_json.keys()
    assert ['access_token', 'token_type', 'expires_in'] == ted_json.keys()

    assert bob_json['access_token'] != ted_json['access_token']
