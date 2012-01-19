import requests

from tests.helpers import (build_authorize_url, parse_query_string,
                           parse_json_response)

# happy path!

def test_should_redirect_to_redirect_uri_argument_passing_auth_token():
    # the default behaviour is to redirect with access token without 
    # any verification.
    # it can be customized using plugins. see usage on 
    # oauth2u/tests/server/test_plugins.py and oauth2u/examples/
    url = build_authorize_url({'client_id': 'client-id',
                               'response_type': 'code',
                               'redirect_uri': 'http://callback'})
    assert_redirect_parameters_keys(url, 'http://callback', ['code'])

# validate required GET arguments

def test_should_require_redirect_uri_argument():
    # if redirect_uri is not provided I can't redirect with GET
    # parameters, then just return 400 and a body with json
    url = build_authorize_url({})
    resp = requests.get(url, allow_redirects=False)
    body = parse_json_response(resp)
    expected_body = {'error': 'invalid_request',
                     'error_description': 'Parameter redirect_uri is required'}

    assert 400 == resp.status_code
    assert expected_body == body


def test_should_require_response_type_argument():
    url = build_authorize_url({'redirect_uri': 'http://callback/return'})
    assert_required_redirect_parameter(url, 'http://callback/return',
                                           'response_type')


def test_should_require_response_type_argument_to_be_code():
    url = build_authorize_url({'redirect_uri': 'http://callback/return',
                               'response_type': 'invalid'})
    expected_params = {'error': 'invalid_request',
                       'error_description': 'Invalid response_type parameter'}
    assert_redirect_parameters(url, 'http://callback/return',
                               expected_params)


def test_should_require_client_id_parameter():
    url = build_authorize_url({'redirect_uri': 'http://callback/return',
                               'response_type': 'code'})
    assert_required_redirect_parameter(url, 'http://callback/return',
                                           'client_id')

# check Location header

def test_should_keep_get_query_string_from_redirect_uri_when_adding_code_parameter():
    url = build_authorize_url({'client_id': 'client-id',
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


def test_should_return_405_on_post_default_behaviour():
    # it could be customized using plugins
    url = build_authorize_url({'client_id': '123',
                               'response_type': 'code',
                               'redirect_uri': 'http://callback'})
    resp = requests.post(url)
    assert 405 == resp.status_code


# custom asserts

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
    assert parameters_keys == params.keys()


def get_parameters_from_redirect(url):
    resp = requests.get(url, allow_redirects=False)
    assert 302 == resp.status_code

    host, params = parse_query_string(resp.headers['Location'])
    return host, params
