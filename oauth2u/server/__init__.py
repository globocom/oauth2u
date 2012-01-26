import uuid
import urllib

import tornado.web
import tornado.ioloop

from oauth2u.server import handlers, plugins, log

class Server(object):

    def __init__(self, port=8000, plugins_directories=(), handlers_directories=(),
                 log_config=None):
        self.port = port
        self.application = None
        self.load_plugins(plugins_directories)
        self.load_handlers(handlers_directories)
        log.configure(**log_config or {})

    @property
    def urls(self):
        return [ url_and_handler for url_and_handler in handlers.items() ]

    def load_plugins(self, directories):
        plugins.load_from_directories(*directories)

    def load_handlers(self, directories):
        handlers.load_from_directories(*directories)

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
        log.info('Server listening on port %s', self.port)
        tornado.ioloop.IOLoop.instance().start()
