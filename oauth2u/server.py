import uuid
import urllib

import tornado.web
import tornado.ioloop

import oauth2u.tokens


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


class Server(object):

    def __init__(self, port=8000):
        self.port = port
        self.application = None

    @property
    def urls(self):
        return [('/authorize', AuthorizationHandler)]

    def start(self):
        self.create_application()
        self.start_ioloop()

    def create_application(self):
        self.application = tornado.web.Application(self.urls, debug=True)
        self.application.listen(self.port)
    
    def start_ioloop(self):
        tornado.ioloop.IOLoop.instance().start()
