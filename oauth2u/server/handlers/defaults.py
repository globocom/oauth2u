# coding: utf-8
import urllib
import urlparse
import base64
import datetime
import re

import tornado

from oauth2u.server import plugins
from oauth2u.server.handlers.register import register
import oauth2u.tokens

from .base import BaseRequestHandler

__all__ = 'AuthorizationHandler', 'AccessTokenHandler', 'add_query_to_url'

@register(r'/authorize')
class AuthorizationHandler(BaseRequestHandler):
    '''
    Handler for the Authorization Request defined in
    http://tools.ietf.org/html/draft-ietf-oauth-v2-22#section-4.1.1

    The default behaviour is to redirect with access token without
    any verification.
    This can (and should) be customized via plugins.

    On errors, GET parameters (`error', `error_description') are provided
    with more information on redirect to `redirect_uri'.
    Unless the error is an invalid/missing `redirect_uri', in this case
    a 400 status code is raises with error information on body.
    
    '''

    supported_response_types = ['code']

    def initialize(self, **kwargs):
        self.code = None
        self.state = None
        self.client_id = None
        self.redirect_uri = None

    def get(self):
        self.load_parameters()
        self.verify_response_type()
        self.create_authorization_token()
        self.save_client_tokens()
        if not plugins.call('authorization-GET', self):
            self.redirect_access_granted(self.client_id, self.code)

    def post(self):
        if not plugins.call('authorization-POST', self):
            self.raise_http_error(405)

    def verify_response_type(self):
        value = self.require_argument('response_type')
        if value not in self.supported_response_types:
            error = {
                'error': 'unsupported_response_type',
                'error_description': 'Supported response_type: code'
                }
            self.raise_http_invalid_argument_error('response_type', error)

    def load_parameters(self):
        self.state = self.get_argument('state', None)
        self.redirect_uri = self.require_argument('redirect_uri')
        self.client_id = self.require_argument('client_id')
        if not self.application.database.find_client(self.client_id):
            self.raise_http_401({'error': 'invalid_client',
                                 'error_description': 'Invalid client_id or code on Authorization header'})

    def raise_http_invalid_argument_error(self, parameter, error):
        if parameter in ['redirect_uri', 'client_id']:
            self.raise_http_400(error)
        else:
            self.raise_http_302(error)

    def create_authorization_token(self):
        self.code = oauth2u.tokens.generate_authorization_code()

    def redirect_access_granted(self, client_id, code):
        '''
        Redirects the user back to ``redirect_uri`` with grant code
        '''
        params = {'code': code }
        state = self.application.database.get_state(client_id,code)
        if state != None:
            params['state'] = state
        
        self.redirect_to_redirect_uri_with_params(params, client_id, code)
    
    def redirect_access_denied(self, client_id, code):
        '''
        Redirects the user back to ``redirect_uri`` with access_denied error
        '''
        params = {
            'error': 'access_denied',
            'error_description': 'The resource owner or authorization server denied the request'
            }
        self.redirect_to_redirect_uri_with_params(params, client_id, code)

    def redirect_unauthorized_client(self, client_id, code):
        params = {
            'error': 'unauthorized_client',
            'error_description': 'The client is not authorized to request an authorization code using this method'
        }
        self.redirect_to_redirect_uri_with_params(params, client_id, code)

    def redirect_temporarily_unavailable(self, client_id, code):
        params = {
            'error': 'temporarily_unavailable',
            'error_description': 'The authorization server is currently unable to handle the request'
            }
        self.redirect_to_redirect_uri_with_params(params, client_id, code)

    def redirect_server_error(self, client_id, code):
        params = {
            'error': 'server_error',
            'error_description': 'The authorization server encountered an unexpected condition which prevented it from fulfilling the request',
            }
        self.redirect_to_redirect_uri_with_params(params, client_id, code)

    def redirect_invalid_scope(self, client_id, code):
        params = {
            'error': 'invalid_scope',
            'error_description': 'The requested scope is invalid, unknown, or malformed'
            }
        self.redirect_to_redirect_uri_with_params(params, client_id, code)

    def redirect_to_redirect_uri_with_params(self, params, client_id, code):
        redirect_uri = self.application.database.get_redirect_uri(client_id, code)
        url = self.build_redirect_uri(params, redirect_uri)
        self.redirect(url)

    def build_redirect_uri(self, params, base_url=None):
        return add_query_to_url(base_url or self.redirect_uri, params)

    def save_client_tokens(self):
        self.application.database.save_new_authorization_code(
            self.code,
            self.client_id,
            self.state,
            redirect_uri=self.redirect_uri)    


@register(r'/access-token')
class AccessTokenHandler(BaseRequestHandler):
    '''
    Handler for the Access Token Request defined in
    http://tools.ietf.org/html/draft-ietf-oauth-v2-22#section-4.1.3

    '''

    required_content_type = "application/x-www-form-urlencoded;charset=UTF-8"

    def post(self):
        self.validate_headers()
        self.load_arguments()
        self.parse_authorization_header()
        self.validate_client_authorization()
        self.build_response()
        self.mark_client_authorization_code_as_used()

    def validate_headers(self):
        self.require_header('content-type', self.required_content_type)
        self.require_header('authorization', startswith='Basic ')

    def load_arguments(self):
        self.require_argument('grant_type', 'authorization_code')
        self.code = self.require_argument('code')
        self.redirect_uri = self.require_argument('redirect_uri')

    def parse_authorization_header(self):
        digest = self.request.headers.get('Authorization')
        digest = re.sub(r'^Basic ', '', digest)
        try:
            digest = base64.b64decode(digest)
        except TypeError:
            self.raise_http_400({'error': 'invalid_request',
                                 'error_description': 'Base 64 from Authorization header could not be decoded'})
        self.client_id, self.code_from_header = digest.split(':')

    def validate_client_authorization(self):
        database = self.application.database
        client = database.find_client(self.client_id)

        if not client:
            self.raise_http_401({'error': 'invalid_client',
                                 'error_description': 'Invalid client_id or code on Authorization header'})

        if not database.client_has_authorization_code(self.client_id, self.code_from_header):
            self.raise_http_401({'error': 'invalid_client',
                                 'error_description': 'Invalid client_id or code on Authorization header'})

        if not database.client_has_authorization_code(self.client_id, self.code):
            self.raise_http_400({'error': 'invalid_grant',
                                 'error_description': 'Invalid code for this client'})

        if not database.client_has_redirect_uri_for_code(self.client_id, self.code, self.redirect_uri):
            self.raise_http_400({'error': 'invalid_grant',
                                 'error_description': 'redirect_uri does not match'})

        if database.is_client_authorization_code_used(self.client_id, self.code):
            self.raise_http_400({'error': 'invalid_grant',
                                 'error_description': 'Authorization grant already used'})

        plugins.call('access-token-validation', self)

    def mark_client_authorization_code_as_used(self):
        self.application.database.mark_client_authorization_code_as_used(self.client_id, self.code)

    def build_response(self):
        response = {
            'access_token': self.build_access_token(),
            'token_type': 'bearer',
            'expires_in': 3600,
            }
        plugins.call('access-token-response', self, response)
        self.write(response)

    def build_access_token(self):
        return oauth2u.tokens.generate_access_token()

    def set_default_headers(self):
        self.set_header('Cache-Control', 'no-store')
        self.set_header('Pragma', 'no-cache')


def add_query_to_url(url, params):
    parts = urlparse.urlparse(url)
    query = dict(urlparse.parse_qsl(parts.query))
    query.update(params)

    return urlparse.urlunparse((parts.scheme, parts.netloc,
                                parts.path, parts.params,
                                urllib.urlencode(query),
                                parts.fragment))
