import urlparse

import requests

from tests.helpers import (build_authorize_url, parse_query_string,
                           parse_json_response)
from asserts import assert_error_redirect_params, assert_status_code

# happy paths!

def test_should_redirect_to_redirect_uri_argument_passing_auth_token():
    url = build_authorize_url({'client_id': 'client-id',
                               'response_type': 'code',
                               'redirect_uri': 'http://callback'})
    assert_redirect_parameters_keys(url, 'http://callback', ['code'])

def test_should_redirect_to_redirect_uri_argument_passing_auth_token_and_state():
    url = build_authorize_url({'client_id': 'client-id',
                               'response_type': 'code',
                               'state': 'my-state',
                               'redirect_uri': 'http://callback'})
    assert_redirect_parameters_keys(url, 'http://callback', ['code','state'])

def test_should_redirect_to_redirect_uri_argument_passing_auth_token_and_state_and_querystring():
    url = build_authorize_url({'client_id': 'client-id',
                               'response_type': 'code',
                               'state': 'my-state',
                               'redirect_uri': 'http://callback?query=string'})
    assert_redirect_parameters_keys(url, 'http://callback', ['code','query','state'])

# validate required GET parameters

def test_should_require_redirect_uri_parameter():
    # if redirect_uri is not provided I can't redirect with GET
    # parameters, then just return 400 and a body with json
    url = build_authorize_url({'client_id': 'client-id'})
    assert_bad_request_for_required_parameter(url, 'redirect_uri')


def test_should_require_client_id_parameter():
    url = build_authorize_url({'redirect_uri': 'http://callback/return'})
    assert_bad_request_for_required_parameter(url, 'client_id')


def test_should_return_401_with_unregistered_client_id():
    url = build_authorize_url({'client_id': 'unregistered-client-id',
                               'redirect_uri': 'http://callback/return'})
    resp = requests.get(url, allow_redirects=False)
    body = parse_json_response(resp)
    expected_body = {'error': 'invalid_client',
                     'error_description': 'Invalid client_id or code on Authorization header'}

    assert 401 == resp.status_code
    assert expected_body == body


def test_should_require_response_type_parameter():
    url = build_authorize_url({'redirect_uri': 'http://callback/return',
                               'client_id': 'client-id'})
    assert_required_redirect_parameter(url, 'http://callback/return',
                                       'response_type')


def test_should_require_response_type_parameter_to_be_code():
    url = build_authorize_url({'redirect_uri': 'http://callback/return',
                               'client_id': 'client-id',
                               'response_type': 'invalid'})
    expected_params = {'error': 'unsupported_response_type',
                       'error_description': 'Supported response_type: code'}
    assert_redirect_parameters(url, 'http://callback/return',
                               expected_params)


# check Location header

def test_should_keep_get_query_string_from_redirect_uri_when_adding_code_parameter():
    url = build_authorize_url({'client_id': 'client-id',
                               'response_type': 'code',
                               'redirect_uri': 'http://callback?param1=value1'})
    resp = requests.get(url, allow_redirects=False)
    assert_status_code(resp, 302)

    url_parts = urlparse.urlparse(resp.headers['location'])
    assert 'callback' == url_parts.netloc
    assert ['code','param1'] == urlparse.parse_qs(url_parts.query).keys()


def test_should_generate_tokens_using_generate_authorization_token_function():
    # tokens generation is stubbed in tests/helpers.py
    url = build_authorize_url({'client_id': '123',
                               'response_type': 'code',
                               'redirect_uri': 'http://callback'})
    resp = requests.get(url, allow_redirects=False)
    assert resp.headers['Location'].startswith('http://callback?code=authorization-code-')


def test_should_return_405_on_post_default_behaviour():
    # it could be customized using plugins
    url = build_authorize_url({'client_id': '123',
                               'response_type': 'code',
                               'redirect_uri': 'http://callback'})
    resp = requests.post(url)
    assert 405 == resp.status_code


# plugins
# test plugins are registered on tests/server/plugins_to_test

def test_should_redirect_to_redirect_uri_with_access_denied_from_plugin():
    # there is a plugin on 'authorization-GET' to ask for user permission
    # and a plugin on 'authorization-POST' to simulate a redirect to 
    # success or error, if user allowed of denied
    # in this test, the user will be denied (see client_id)

    http = requests.session()
    url = build_authorize_url({'client_id': 'client-id-verify-access',
                               'response_type': 'code',
                               'redirect_uri': 'http://callback'})
    resp = http.get(url)

    # make sure GET plugin overrides default redirect
    assert 200 == resp.status_code
    assert 'Hello resource owner, do you allow this client to access your resources?' in resp.content

    # simulares a POST denying access from user
    resp = http.post(url, data={'allow': 'no'})
    assert_error_redirect_params(resp, 'http://callback',
                                 'access_denied',
                                 'The resource owner or authorization server denied the request')


def test_should_redirect_with_unauthorized_client_error_if_client_id_cant_request_authorization():
    url = build_authorize_url({'client_id': 'unauthorized-client',
                               'response_type': 'code',
                               'redirect_uri': 'http://callback'})
    resp = requests.get(url, allow_redirects=False)
    assert_error_redirect_params(resp, 'http://callback',
                                 'unauthorized_client',
                                 'The client is not authorized to request an authorization code using this method')


def test_should_redirect_with_temporarily_unavailable_error():
    url = build_authorize_url({'client_id': 'temporarily_unavailable',
                               'response_type': 'code',
                               'redirect_uri': 'http://callback'})
    resp = requests.get(url, allow_redirects=False)
    assert_error_redirect_params(resp, 'http://callback',
                                 'temporarily_unavailable',
                                 'The authorization server is currently unable to handle the request')

def test_should_redirect_with_server_error_error():
    url = build_authorize_url({'client_id': 'server_error',
                               'response_type': 'code',
                               'redirect_uri': 'http://callback'})
    resp = requests.get(url, allow_redirects=False)
    assert_error_redirect_params(resp, 'http://callback',
                                 'server_error',
                                 'The authorization server encountered an unexpected condition which prevented it from fulfilling the request')

def test_should_redirect_with_invalid_scope_error():
    url = build_authorize_url({'client_id': 'invalid_scope',
                               'response_type': 'code',
                               'redirect_uri': 'http://callback'})
    resp = requests.get(url, allow_redirects=False)
    assert_error_redirect_params(resp, 'http://callback',
                                 'invalid_scope',
                                 'The requested scope is invalid, unknown, or malformed')


def test_should_redirect_to_redirect_uri_with_authorization_code_from_plugin():
    http = requests.session()
    url = build_authorize_url({'client_id': 'client-id-verify-access',
                               'response_type': 'code',
                               'redirect_uri': 'http://callback'})
    resp = http.get(url)

    assert 200 == resp.status_code
    assert 'Hello resource owner, do you allow this client to access your resources?' in resp.content

    resp = http.post(url, data={'allow': 'yes'})

    assert_status_code(resp, 302)
    assert resp.headers['Location'].startswith('http://callback?code=authorization-code-')


# custom asserts
def assert_bad_request_for_required_parameter(url, missing_parameter):
    resp = requests.get(url, allow_redirects=False)
    body = parse_json_response(resp)
    expected_body = {'error': 'invalid_request',
                     'error_description': 'Parameter %s is required' % missing_parameter}

    assert 400 == resp.status_code
    assert expected_body == body

def assert_required_redirect_parameter(url, redirect_uri, parameter):
    expected_params = {
        'error': 'invalid_request',
        'error_description': 'Parameter {0} is required'.format(parameter)
        }
    assert_redirect_parameters(url, redirect_uri, expected_params)

def assert_redirect_parameters(url, redirect_uri, expected_params):
    host, params = get_parameters_from_redirect(url)
    assert redirect_uri == host
    assert expected_params == params

def assert_redirect_parameters_keys(url, redirect_uri, parameters_keys):
    host, params = get_parameters_from_redirect(url)
    assert redirect_uri == host
    assert sorted(parameters_keys) == sorted(params.keys())

def get_parameters_from_redirect(url):
    resp = requests.get(url, allow_redirects=False)
    assert 302 == resp.status_code

    host, params = parse_query_string(resp.headers['Location'])
    return host, params
