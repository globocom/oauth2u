import sys
import urllib
from os.path import dirname, join, abspath

import oauth2u
import oauth2u.tokens

oauth2u.tokens.generate_authorization_code = lambda: '123-abc'
oauth2u.tokens.generate_access_token = lambda: '321-access-token'


if __name__ == '__main__':
    plugins = abspath(join(dirname(__file__), 'server', 'plugins_to_test'))
    oauth2u.server.plugins.load_from_directories(plugins)

    server = oauth2u.server.Server(port=8888)
    server.start()
