'''
This server is started before all tests are executed, and stopped afterwards

There are plugins and url handlers registered just for testing purposes, see
the ``plugins_directories`` and ``handlers_directories`` parameters
 passed to ``Server()``

Token generation is stubbed to produce deterministic values.

'''

import sys
import urllib
import uuid
import signal
from os.path import dirname, join, abspath

import oauth2u
import oauth2u.tokens

def die(*args, **kw):
    print "Captured SIGINT, exiting normally to save coverage"
    exit(0)

signal.signal(signal.SIGINT, die)

# stubs
oauth2u.tokens.generate_authorization_code = lambda: 'authorization-code-{0}'.format(str(uuid.uuid4()))
oauth2u.tokens.generate_access_token = lambda: 'access-token-{0}'.format(str(uuid.uuid4()))

if __name__ == '__main__':
    plugins = abspath(join(dirname(__file__), 'server', 'plugins_to_test'))
    handlers = abspath(join(dirname(__file__), 'server', 'handlers_to_test'))
    logfile = abspath(join(dirname(__file__), 'server.log'))

    server = oauth2u.server.Server(port=8888,
                                   plugins_directories=[plugins],
                                   handlers_directories=[handlers],
                                   log_config={'filename': logfile})
    print 'Listening on 8888'
    server.start()
