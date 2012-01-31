import tornado
from oauth2u.server import handlers

@handlers.register('/test/dummy-url')
class DummyHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Dummy handler")


@handlers.register('/test/faulty-url')
class FaultyHandler(handlers.base.BaseRequestHandler):
    def get(self):
        self.send_error(status_code=500)
