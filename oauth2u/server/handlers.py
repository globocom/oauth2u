# coding: utf-8
import urllib
import base64

import tornado

from oauth2u.server import database
import oauth2u.tokens

class BaseRequestHandler(tornado.web.RequestHandler):

    def require_argument(self, name, expected_value=None):
        value = self.get_argument(name, None)
        if value is None:
            self.raise_http_400({'error': 'invalid_request',
                                 'error_description': u'Parameter {0} is required'.format(name)})

        if expected_value and value != expected_value:
            self.raise_http_400({'error': 'invalid_request',
                                 'error_description': u'Parameter {0} should be {1}'.format(name, expected_value)})
        return value

    def require_header(self, name, expected_value=None, startswith=None):
        value = self.request.headers.get(name)
        if value is None:
            self.raise_http_400({'error': 'invalid_request',
                                 'error_description': u'Header {0} is required'.format(name)})

        if expected_value and value != expected_value:
            self.raise_http_400({'error': 'invalid_request',
                                 'error_description': u'Header {0} should be {1}'.format(name, expected_value)})

        if startswith and not value.startswith(startswith):
            self.raise_http_400({'error': 'invalid_request',
                                 'error_description': u'Header {0} should start with "{1}"'.format(name, startswith)})

        return value

    def raise_http_400(self, response_body):
        error = tornado.web.HTTPError(400, '')
        error.response_body = response_body
        raise error

    def get_error_html(self, status_code, exception, **kwargs):
        ''' Called by tornado to fill error response body '''
        if hasattr(exception, 'response_body'):
            self.write(exception.response_body)


class AuthorizationHandler(BaseRequestHandler):
    '''
    Handler for the Authorization Request defined in
    http://tools.ietf.org/html/draft-ietf-oauth-v2-22#section-4.1.1
    
    '''

    def get(self):
        self.validate_arguments()
        self.load_arguments()
        self.create_authorization_token()
        self.redirect_with_token()
        self.save_authorization_token()

    def validate_arguments(self):
        ''' Currently only ``code`` is supported '''
        self.require_argument('response_type', 'code')

    def load_arguments(self):
        self.client_id = self.require_argument('client_id')
        self.redirect_uri = self.require_argument('redirect_uri')

    def create_authorization_token(self):
        self.code = oauth2u.tokens.generate_authorization_code()

    def redirect_with_token(self):
        params = {'code': self.code}
        prefix = '?' if '?' not in self.redirect_uri else '&'
        self.redirect(self.redirect_uri + prefix + urllib.urlencode(params))

    def save_authorization_token(self):
        database.save_authorization(self.code, self.client_id, self.redirect_uri)

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
        self.validate_authorization()
        self.build_response()
        self.mark_authorization_as_used()
                
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
        self.client_id, code = base64.b64decode(digest).split(':')

    def validate_authorization(self):
        authorization = database.find_authorization(self.code)
        if not authorization:
            self.raise_http_400({'error': 'invalid_grant',
                                 'error_description': 'Code not found'})
        if authorization['redirect_uri'] != self.redirect_uri:
            self.raise_http_400({'error': 'invalid_grant',
                                 'error_description': 'redirect_uri does not match'})
        if database.is_code_used(self.code):
            self.raise_http_400({'error': 'invalid_grant',
                                 'error_description': 'authorization grant already used'})

    def mark_authorization_as_used(self):
        database.mark_as_used(self.code)

    def build_response(self):
        self.write({
                'access_token': self.build_access_token(),
                'expires_in': 3600,
                })

    def build_access_token(self):
        return oauth2u.tokens.generate_access_token()
