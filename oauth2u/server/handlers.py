# coding: utf-8
import urllib
import base64

import tornado

from oauth2u.server import database
import oauth2u.tokens

class BaseRequestHandler(tornado.web.RequestHandler):

    def require_argument(self, name, expected_value):
        value = self.get_argument(name)
        if value != expected_value:
            self.invalid_argument('{0} should be {1}'.format(name, expected_value))

    def invalid_argument(self, message):
        self.raise_http_400(message)

    def invalid_header(self, message):
        self.raise_http_400(message)

    def raise_http_400(self, message):
        raise tornado.web.HTTPError(400, message)


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
        self.client_id = self.get_argument('client_id')
        self.redirect_uri = self.get_argument('redirect_uri')

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
        self.build_response()

    def build_response(self):
        self.set_header('Content-Type', 'application/json;charset=UTF-8')
        self.write({
                'access_token': self.build_access_token(),
                'expires_in': 3600,
                })

    def validate_headers(self):
        if self.request.headers.get('content-type') != self.required_content_type:
            self.invalid_header("Content-Type header should be {0}"
                                .format(self.required_content_type))

        authorization =  self.request.headers.get('Authorization', '')
        if not authorization.startswith('Basic '):
            self.invalid_header("Basic Authorization header is required")

    def load_arguments(self):
        self.require_argument('grant_type', 'authorization_code')
        self.code = self.get_argument('code')
        self.redirect_uri = self.get_argument('redirect_uri')

    def parse_authorization_header(self):
        digest = self.request.headers.get('Authorization')
        digest = digest.lstrip('Basic ')
        self.client_id, code = base64.b64decode(digest).split(':')

    def build_access_token(self):
        return oauth2u.tokens.generate_access_token()
