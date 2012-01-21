import requests

from tests.helpers import (build_authorize_url, parse_query_string,
                           parse_json_response)

# happy paths!

def test_should_redirect_to_redirect_uri_argument_passing_auth_token():
    # the default behaviour is to redirect with access token without 
    # any verification.
    # it can be customized using plugins. see usage on 
    # oauth2u/tests/server/test_plugins.py and oauth2u/examples/
    url = build_authorize_url({'client_id': 'client-id',
                               'response_type': 'code',
                               'redirect_uri': 'http://callback'})
    assert_redirect_parameters_keys(url, 'http://callback', ['code'])

def test_should_redirect_to_redirect_uri_with_access_denied_from_plugin():
    http = requests.session()

    # there is a plugin on 'authorization-GET' to ask for user permission
    # and a plugin on 'authorization-POST' to simulate a redirect to 
    # success or error, if user allowed of denied
    url = build_authorize_url({'client_id': 'client-id-access-denied',
                               'response_type': 'code',
                               'redirect_uri': 'http://callback'})
    resp = http.get(url, allow_redirects=False)

    # make sure GET plugin works and no default redirect is done

    assert 200 == resp.status_code
    assert 'Hello resource owner, do you allow this client to access your resources?' in resp.content

    # simulares a POST denying access from user
    resp = http.post(url, data={'allow': 'no'})
    assert 302 == resp.status_code

    expected_params = {
        'code': 'access_denied',
        'error_description': 'The resource owner or authorization server denied the request'
        }
    url, params = parse_query_string(resp.headers['location'])
    assert 'http://callback' == url
    assert expected_params == params


# validate required GET parameters

def test_should_require_redirect_uri_parameter():
    # if redirect_uri is not provided I can't redirect with GET
    # parameters, then just return 400 and a body with json
    url = build_authorize_url({})
    resp = requests.get(url, allow_redirects=False)
    body = parse_json_response(resp)
    expected_body = {'error': 'invalid_request',
                     'error_description': 'Parameter redirect_uri is required'}

    assert 400 == resp.status_code
    assert expected_body == body


def test_should_require_response_type_parameter():
    url = build_authorize_url({'redirect_uri': 'http://callback/return'})
    assert_required_redirect_parameter(url, 'http://callback/return',
                                       'response_type')


def test_should_require_response_type_parameter_to_be_code():
    url = build_authorize_url({'redirect_uri': 'http://callback/return',
                               'response_type': 'invalid'})
    expected_params = {'error': 'invalid_request',
                       'error_description': 'Parameter response_type should be code'}
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


# plugins
# test plugins are registered on tests/server/plugins_to_test

def test_using_authorization_GET_plugin_to_execute_on_authorization_request_GET_method():
    url = build_authorize_url({'client_id': 'client-id-from-plugins-test',
                               'response_type': 'code',
                               'redirect_uri': 'http://example.com/return'})
    resp = requests.get(url, allow_redirects=False)

    assert 200 == resp.status_code
    assert u"I'm a dummy plugin doing nothing on GET" == resp.content


def test_using_authorization_POST_plugin_to_execute_on_authorization_request_POST_method():
    http = requests.session()
    url = build_authorize_url({'client_id': 'client-id-from-plugins-test',
                               'response_type': 'code',
                               'redirect_uri': 'http://example.com/return'})
    http.get(url)
    resp = http.post(url)

    assert 200 == resp.status_code
    assert u"I'm a dummy plugin doing nothing on POST" == resp.content


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
