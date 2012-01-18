'''
This server is started before all tests are executed, and stopped afterwards

There are plugins and url handlers registered just for testing purposes, see
the ``plugins_directories`` and ``handlers_directories`` parameters
 passed to ``Server()``

Token generation is stubbed to produce deterministic values.

'''

import sys
import urllib
from os.path import dirname, join, abspath

import oauth2u
import oauth2u.tokens

oauth2u.tokens.generate_authorization_code = lambda: 'am3jah7dl'
oauth2u.tokens.generate_access_token = lambda: '321-access-token'


if __name__ == '__main__':
    plugins = abspath(join(dirname(__file__), 'server', 'plugins_to_test'))
    handlers = abspath(join(dirname(__file__), 'server', 'handlers_to_test'))

    server = oauth2u.server.Server(port=8888,
                                   plugins_directories=[plugins],
                                   handlers_directories=[handlers])
    print 'Listening on 8888'
    server.start()
