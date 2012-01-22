import json

import pytest

from tests.helpers import parse_json_response, parse_query_string


__all__ = ('assert_valid_access_token',
           'assert_error_response_body',
           'assert_unauthorized',
           'assert_has_no_cache_headers')


def assert_valid_access_token(response):
    body = parse_json_response(response)

    assert 200 == response.status_code
    assert ['access_token', 'token_type', 'expires_in'] == body.keys()
    assert body['access_token'].startswith('access-token-')
    assert 'bearer' == body['token_type']
    assert_has_no_cache_headers(response)

def assert_error_response_body(response, error, error_description):
    body = parse_json_response(response)
    expected_body = {
        'error': error,
        'error_description': error_description
        }

    assert 400 == response.status_code
    assert expected_body == body
    assert_has_no_cache_headers(response)

def assert_error_redirect_params(response, redirect_uri, error, error_description):
    assert_status_code(response, 302)

    url, params = parse_query_string(response.headers['location'])
    expected_params = {
        'error': error,
        'error_description': error_description
        }

    assert redirect_uri == url
    assert expected_params == params

def assert_unauthorized(response):
    expected_response = {
        'error': 'invalid_client',
        'error_description': 'Invalid client_id or code on Authorization header',
    }
    assert 401 == response.status_code
    assert expected_response == parse_json_response(response)
    assert 'Basic realm="OAuth 2.0 Secure Area"' == response.headers.get('WWW-Authenticate')
    assert_has_no_cache_headers(response)

def assert_has_no_cache_headers(response):
    assert 'no-store' == response.headers.get('Cache-Control')
    assert 'no-cache' == response.headers.get('Pragma')

def assert_status_code(response, status_code):
    if response.status_code != status_code:
        pytest.fail("Invalid response code {0} on '{1}' should be {2}.\n"
                    "response body: '{3}'\n"
                    "response headers: {4}"
                    .format(response.status_code,
                            response.url,
                            status_code,
                            response.content,
                            response.headers))
