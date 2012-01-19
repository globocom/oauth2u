import json

import requests


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

