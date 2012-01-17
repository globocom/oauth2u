import uuid
import urllib

import tornado.web
import tornado.ioloop

from .handlers import AuthorizationHandler, AccessTokenHandler

class Server(object):

    def __init__(self, port=8000):
        self.port = port
        self.application = None

    @property
    def urls(self):
        return ((r'/authorize', AuthorizationHandler),
                (r'/access-token', AccessTokenHandler))

    def start(self):
        self.create_application()
        self.start_ioloop()

    def create_application(self):
        self.application = tornado.web.Application(self.urls,
                                                   **self.application_settings)
        self.application.listen(self.port)
    
    @property
    def application_settings(self):
        return dict(debug=True,
                    cookie_secret=str(uuid.uuid4()))

    def start_ioloop(self):
        tornado.ioloop.IOLoop.instance().start()
