import sys
import urllib

import oauth2u
import oauth2u.tokens

oauth2u.tokens.generate_authorization_code = lambda: '123-abc'
oauth2u.tokens.generate_access_token = lambda: '321-access-token'

class OAuthStubServer(oauth2u.Server):
    pass


if __name__ == '__main__':
    server = OAuthStubServer(port=8888)
    server.start()
