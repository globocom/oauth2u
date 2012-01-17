import tornado
from oauth2u.server import handlers

@handlers.register('/test/dummy-url')
class DummyHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Dummy handler")

