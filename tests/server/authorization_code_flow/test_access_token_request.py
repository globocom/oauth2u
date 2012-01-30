import requests
import pytest

from tests.helpers import *
from asserts import *

CONTENT_TYPE = 'application/x-www-form-urlencoded;charset=UTF-8'
HEADERS = {
    'Content-Type': CONTENT_TYPE,
    'Authorization': 'Basic MTIzOmZvbw==',
    }


# happy path!

URL = build_access_token_url()

def test_happy_path_should_return_access_token_if_valid_authorization_code():
    # tokens generation is stubbed in tests/helpers.py
    code = request_authorization_code('client-id')
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://callback'
        }
    valid_headers = {
        'Content-Type': CONTENT_TYPE,
        'Authorization': build_basic_authorization_header('client-id', code)
        }
    response = requests.post(URL, data=data, headers=valid_headers)

    assert_valid_access_token(response)


# validates required headers

def test_should_require_content_type_header():
    response = requests.post(URL)
    assert_error_response_body(response,
                          'invalid_request',
                          'Header content-type is required')


def test_should_require_content_type_header_to_be_x_wwww_form_urlencoded():
    response = requests.post(URL, headers={'Content-Type': 'text/plain'})
    assert_error_response_body(response,
                          'invalid_request',
                          'Header content-type should be '+CONTENT_TYPE)


def test_should_require_authorization_header():
    response = requests.post(URL, headers={'Content-Type': CONTENT_TYPE})
    assert_error_response_body(response,
                          'invalid_request',
                          'Header authorization is required')


def test_authorization_header_should_be_basic():
    response = requests.post(URL, headers={'Content-Type': CONTENT_TYPE,
                                           'Authorization': 'Invalid Basic Header'})
    assert_error_response_body(response,
                          'invalid_request',
                          'Header authorization should start with "Basic "')


def test_should_return_400_with_invalid_request_error_if_base64_header_could_not_be_decoded():
    data = {
        'grant_type': 'authorization_code',
        'code': 'ccc',
        'redirect_uri': 'http://callback'
        }
    invalid_headers = {
        'Content-Type': CONTENT_TYPE,
        'Authorization': 'Basic this-is-not-base-64',
        }
    response = requests.post(URL, data=data, headers=invalid_headers)
    assert_error_response_body(response,
                          'invalid_request',
                          'Base 64 from Authorization header could not be decoded')


@pytest.mark.xfail
def test_should_return_400_with_invalid_request_error_if_base64_header_is_not_in_the_correct_format():
    # should be "string:string"
    assert 0


# validates required POST parameters

def test_should_require_grant_type_argument():
    response = requests.post(URL, data={}, headers=HEADERS)
    assert_error_response_body(response,
                          'invalid_request',
                          'Parameter grant_type is required')


def test_should_require_grant_type_argument_to_be_authorization_code():
    response = requests.post(URL, data={'grant_type': 'invalid'},
                             headers=HEADERS)
    assert_error_response_body(response,
                          'invalid_request',
                          'Parameter grant_type should be authorization_code')


def test_should_require_code_argument():
    response = requests.post(URL, data={'grant_type': 'authorization_code'},
                             headers=HEADERS)
    assert_error_response_body(response,
                          'invalid_request',
                          'Parameter code is required')


def test_should_require_redirect_uri_argument():
    response = requests.post(URL, data={'grant_type': 'authorization_code',
                                        'code': 'foo'},
                             headers=HEADERS)
    assert_error_response_body(response,
                          'invalid_request',
                          'Parameter redirect_uri is required')


@pytest.mark.xfail
def test_should_return_400_if_invalid_body_format():
    # the client could send the correct headers but invalid body format
    assert 0


# all possible errors for access token request

def test_should_return_401_with_invalid_client_error_if_invalid_client_id_on_Authorization_header():
    code = request_authorization_code('client-id')
    data = {'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': 'http://callback'}
    invalid_headers = {
        'Content-Type': CONTENT_TYPE,
        'Authorization': build_basic_authorization_header('INCORREECT-CLIENT-ID', code)
        }
    response = requests.post(URL, data=data, headers=invalid_headers)
    assert_unauthorized(response)


def test_should_return_401_with_invalid_client_error_if_invalid_code_on_Authorization_header():
    code = request_authorization_code('client-id')
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://callback',
        }
    invalid_headers = {
        'Content-Type': CONTENT_TYPE,
        'Authorization': build_basic_authorization_header('client-id', 'INVALIDCODE')
        }
    response = requests.post(URL, data=data, headers=invalid_headers)
    assert_unauthorized(response)


def test_should_return_400_with_invalid_grant_error_if_code_from_body_was_not_found():
    # there is a code for this client and the authorization header is valid, but
    # the code informed on body is not the correct code
    code = request_authorization_code('client-id')
    data = {
        'grant_type': 'authorization_code',
        'code': 'INVALID-CODE',
        'redirect_uri': 'http://callback',
        }
    valid_headers = {
        'Content-Type': CONTENT_TYPE,
        'Authorization': build_basic_authorization_header('client-id', code)
        }
    response = requests.post(URL, data=data, headers=valid_headers)
    assert_error_response_body(response,
                          'invalid_grant',
                          'Invalid code for this client')


def test_should_return_invalid_grant_error_if_redirect_uri_is_invalid():
    # the redirect uri informed on body is not the same informed when the code 
    # was created
    code = request_authorization_code('client-id',
                                      redirect_uri='http://example.com')
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://callback', # different uri
        }
    valid_headers = {
        'Content-Type': CONTENT_TYPE,
        'Authorization': build_basic_authorization_header('client-id', code)
        }
    response = requests.post(URL, data=data, headers=valid_headers)
    assert_error_response_body(response,
                          'invalid_grant',
                          'redirect_uri does not match')


def test_should_return_invalid_grant_if_duplicate_access_token_request_with_same_authorization_grant():
    code = request_authorization_code('client-id')
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://callback'
        }
    valid_headers = {
        'Content-Type': CONTENT_TYPE,
        'Authorization': build_basic_authorization_header('client-id', code)
        }

    response = requests.post(URL, data=data, headers=valid_headers)
    assert_valid_access_token(response)

    response = requests.post(URL, data=data, headers=valid_headers)
    assert_error_response_body(response,
                          'invalid_grant',
                          'Authorization grant already used')


# multiple users authenticating

def test_multiple_users_should_be_able_to_authenticate():
    yield ("using same client id",
           check_multiple_users_with_client_ids, 'client-id', 'client-id')
    yield ("using different client ids",
           check_multiple_users_with_client_ids, 'bob-client-id', 'ted-client-id')

def check_multiple_users_with_client_ids(bob_client_id, ted_client_id):
    bob_code = request_authorization_code(bob_client_id)
    ted_code = request_authorization_code(ted_client_id)

    bob_data = {
        'grant_type': 'authorization_code',
        'code': bob_code,
        'redirect_uri': 'http://callback'
        }
    ted_data = {
        'grant_type': 'authorization_code',
        'code': ted_code,
        'redirect_uri': 'http://callback'
        }

    bob_response = requests.post(URL, data=bob_data, headers={
            'Content-Type': CONTENT_TYPE,
            'Authorization': build_basic_authorization_header(bob_client_id, bob_code)
            })
    ted_response = requests.post(URL, data=ted_data, headers={
            'Content-Type': CONTENT_TYPE,
            'Authorization': build_basic_authorization_header(ted_client_id, ted_code)
            })

    assert_valid_access_token(bob_response)
    assert_valid_access_token(ted_response)


# plugins
# test plugins are registered on tests/server/plugins_to_test

def test_should_allow_json_response_customization_via_plugin():
    client_id = 'client-id-from-access-token-tests'
    code = request_authorization_code(client_id)
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://callback'
        }
    valid_headers = {
        'Content-Type': CONTENT_TYPE,
        'Authorization': build_basic_authorization_header(client_id, code)
        }
    response = requests.post(URL, data=data, headers=valid_headers)
    body = parse_json_response(response)

    assert 200 == response.status_code
    assert 'Igor Sobreira' == body.get('user_name','')

def test_should_allow_custom_validation_via_plugin():
    client_id = 'rejected-client-id'
    code = request_authorization_code(client_id)
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://callback'
        }
    valid_headers = {
        'Content-Type': CONTENT_TYPE,
        'Authorization': build_basic_authorization_header(client_id, code)
        }
    response = requests.post(URL, data=data, headers=valid_headers)

    assert_error_response_body(response,
                          'invalid_request',
                          'My plugin rejected your request')

