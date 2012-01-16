# coding: utf-8
import urllib
import base64

import tornado

from oauth2u.server import database
import oauth2u.tokens

class BaseRequestHandler(tornado.web.RequestHandler):
    def invalid_argument(self, message):
        self.raise_http_400(message)

    def invalid_header(self, message):
        self.raise_http_400(message)

    def raise_http_400(self, message):
        raise tornado.web.HTTPError(400, message)


class AuthorizationHandler(tornado.web.RequestHandler):
    '''
    Handler for the Authorization Request defined in
    http://tools.ietf.org/html/draft-ietf-oauth-v2-22#section-4.1.1
    
    '''

    def get(self):
        self.validate_response_type()
        client_id = self.get_argument('client_id')
        redirect_uri = self.get_argument('redirect_uri')
        code = self.create_code()
        self.redirect_with_code(code, redirect_uri)
        self.save_code(client_id, code, redirect_uri)

    def validate_response_type(self):
        ''' Currently only ``code`` is supported '''
        response_type = self.get_argument('response_type')
        if response_type != 'code':
            raise tornado.web.HTTPError(400, "response_type should be code")

    def create_code(self):
        return oauth2u.tokens.generate_authorization_code()

    def redirect_with_code(self, code, redirect_uri):
        params = {'code': code}
        prefix = '?' if '?' not in redirect_uri else '&'
        self.redirect(redirect_uri + prefix + urllib.urlencode(params))

    def save_code(self, code, client_id, redirect_uri):
        database.new_authorization(code, client_id, redirect_uri)

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
        self.grant_type = self.get_argument('grant_type')
        if self.grant_type != 'authorization_code':
            self.invalid_argument("grant_type should be authorization_code")
        self.code = self.get_argument('code')
        self.redirect_uri = self.get_argument('redirect_uri')

    def parse_authorization_header(self):
        digest = self.request.headers.get('Authorization')
        digest = digest.lstrip('Basic ')
        self.client_id, code = base64.b64decode(digest).split(':')

    def build_access_token(self):
        return oauth2u.tokens.generate_access_token()
