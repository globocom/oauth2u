# coding: utf-8
import urllib
import base64
import datetime
import re

import tornado

from oauth2u.server import database, plugins
from oauth2u.server.handlers.register import register
import oauth2u.tokens

from .base import BaseRequestHandler

__all__ = 'AuthorizationHandler', 'AccessTokenHandler'

@register(r'/authorize')
class AuthorizationHandler(BaseRequestHandler):
    '''
    Handler for the Authorization Request defined in
    http://tools.ietf.org/html/draft-ietf-oauth-v2-22#section-4.1.1
    
    '''

    def initialize(self, **kwargs):
        self.code = None
        self.client_id = None
        self.redirect_uri = None
        self.response_type = None

    def get(self):
        self.load_parameters()
        self.create_authorization_token()
        self.save_client_tokens()
        if not plugins.call('authorization-GET', self):
            self.redirect_with_token()

    def post(self):
        if not plugins.call('authorization-POST', self):
            self.raise_http_error(405)

    def load_parameters(self):
        self.redirect_uri = self.require_argument('redirect_uri')
        self.response_type = self.require_argument('response_type', 'code')
        self.client_id = self.require_argument('client_id')

    def raise_http_invalid_argument_error(self, parameter, error):
        if parameter == 'redirect_uri':
            self.raise_http_400(error)
        else:
            self.raise_http_302(error)

    def create_authorization_token(self):
        self.code = oauth2u.tokens.generate_authorization_code()

    def redirect_with_token(self):
        self.redirect(self.build_success_redirect_uri())

    def build_success_redirect_uri(self):
        return self.build_redirect_uri({'code': self.code})

    def build_redirect_uri(self, params):
        prefix = '?' if '?' not in self.redirect_uri else '&'
        return self.redirect_uri + prefix + urllib.urlencode(params)

    def save_client_tokens(self):
        database.save_new_authorization_code(
            self.code,
            self.client_id,
            redirect_uri=self.redirect_uri,
            redirect_uri_with_code=self.build_success_redirect_uri())


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

    def mark_client_authorization_code_as_used(self):
        database.mark_client_authorization_code_as_used(self.client_id, self.code)

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
        self.set_header('Pragma', 'no-store')
