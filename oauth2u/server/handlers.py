import urllib

import tornado

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
        self.get_argument('client_id')
        redirect_uri = self.get_argument('redirect_uri') # XXX
        self.redirect_with_code(redirect_uri)

    def redirect_with_code(self, redirect_uri):
        params = {'code': oauth2u.tokens.generate_authorization_code()}
        prefix = '?' if '?' not in redirect_uri else '&'
        self.redirect(redirect_uri + prefix + urllib.urlencode(params))

    def validate_response_type(self):
        ''' Currently only ``code`` is supported '''
        response_type = self.get_argument('response_type')
        if response_type != 'code':
            raise tornado.web.HTTPError(400, "response_type should be code")


class AccessTokenHandler(BaseRequestHandler):
    '''
    Handler for the Access Token Request defined in
    http://tools.ietf.org/html/draft-ietf-oauth-v2-22#section-4.1.3

    '''

    required_content_type = "application/x-www-form-urlencoded;charset=UTF-8"

    def post(self):
        self.validate_headers()
        self.load_arguments()

    def validate_headers(self):
        if self.request.headers.get('content-type') != self.required_content_type:
            self.invalid_header("Content-Type header should be {0}".format(self.required_content_type))

    def load_arguments(self):
        self.grant_type = self.get_argument('grant_type')
        if self.grant_type != 'authorization_code':
            self.invalid_argument("grant_type should be authorization_code")
        self.code = self.get_argument('code')
        self.redirect_uri = self.get_argument('redirect_uri')
