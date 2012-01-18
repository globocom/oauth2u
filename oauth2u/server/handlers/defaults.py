# coding: utf-8
import urllib
import base64
import datetime

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

    def get(self):
        self.validate_arguments()
        self.load_arguments()
        self.create_authorization_token()
        self.save_client_tokens()
        if not plugins.call('authorization-GET', self):
            self.redirect_with_token()

    def post(self):
        plugins.call('authorization-POST', self)

    def validate_arguments(self):
        ''' Currently only ``code`` is supported '''
        self.require_argument('response_type', 'code')

    def load_arguments(self):
        self.client_id = self.require_argument('client_id')
        self.redirect_uri = self.require_argument('redirect_uri')

    def create_authorization_token(self):
        self.code = oauth2u.tokens.generate_authorization_code()

    def redirect_with_token(self):
        self.redirect(self.build_redirect_uri())

    def build_redirect_uri(self):
        params = {'code': self.code}
        prefix = '?' if '?' not in self.redirect_uri else '&'
        return self.redirect_uri + prefix + urllib.urlencode(params)

    def save_client_tokens(self):
        database.save_client_information(
            self.client_id,
            authorization_code=self.code,
            authorization_code_generation_date=datetime.datetime.utcnow(),
            redirect_uri=self.redirect_uri,
            redirect_uri_with_code=self.build_redirect_uri())


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
        digest = digest.lstrip('Basic ')
        try:
            digest = base64.b64decode(digest)
        except TypeError:
            self.raise_http_400({'error': 'invalid_request',
                                 'error_description': 'Base 64 from Authorization header could not be decoded'})
        self.client_id, code = digest.split(':')

    def validate_client_authorization(self):
        client = database.find_client(self.client_id)

        if not client:
            # TODO: this verification should looks for clients registration
            self.raise_http_401({'error': 'invalid_client',
                                 'error_description': 'Invalid client_id or code on Authorization header'})

        if not client.get('authorization_code'):
            self.raise_http_400({'error': 'invalid_grant',
                                 'error_description': 'Code not found'})

        if client['authorization_code'] != self.code:
            self.raise_http_400({'error': 'invalid_grant',
                                 'error_description': 'Code not found'})

        if client['redirect_uri'] != self.redirect_uri:
            self.raise_http_400({'error': 'invalid_grant',
                                 'error_description': 'redirect_uri does not match'})

        if database.is_authorization_code_used(self.client_id):
            self.raise_http_400({'error': 'invalid_grant',
                                 'error_description': 'authorization grant already used'})

    def mark_client_authorization_code_as_used(self):
        database.mark_authorization_code_as_used(self.client_id)

    def build_response(self):
        self.write({
                'access_token': self.build_access_token(),
                'expires_in': 3600,
                })

    def build_access_token(self):
        return oauth2u.tokens.generate_access_token()
