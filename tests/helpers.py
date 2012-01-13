import sys
import urllib

import oauth2u
import oauth2u.tokens

oauth2u.tokens.generate_authorization_code = lambda: '123-abc'

class OAuthStubServer(oauth2u.Server):
    pass


if __name__ == '__main__':
    if 'start_test_server' in sys.argv:
        server = OAuthStubServer(port=8888)
        server.start()
