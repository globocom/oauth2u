import uuid
import urllib

import tornado.web
import tornado.ioloop

from .handlers import AuthorizationHandler

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
