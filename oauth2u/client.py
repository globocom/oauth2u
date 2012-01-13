# coding: utf-8
import urllib

from tornado import httpclient
from tornado.web import RequestHandler, Application, asynchronous
from tornado.ioloop import IOLoop
from tornado.auth import OAuth2Mixin
from tornado.httputil import url_concat

CLIENT_ID = "client-id"
HOST = 'http://oauth.client:8000'
REDIRECT_URI = HOST + '/return'

class Home(RequestHandler, OAuth2Mixin):

    _OAUTH_AUTHORIZE_URL = "http://auth.server:8008/authorize"

    def get(self):
        self.authorize_redirect(redirect_uri=REDIRECT_URI,
                                client_id=CLIENT_ID)

class Return(RequestHandler):

    _OAUTH_ACCESS_TOKEN_URL = "http://auth.server:8008/access-token"

    @asynchronous
    def get(self):
        self.fetch_access_token()

    def fetch_access_token(self):
        http = httpclient.AsyncHTTPClient()
        http.fetch(self.access_token_url,
                   method='POST',
                   body=self.build_params(),
                   callback=self.async_callback(self.on_access_token))

    def build_params(self):
        params = {
            'grant_type': 'authorization_code',
            'code': self.get_argument('code'),
            'redirect_uri': REDIRECT_URI,
            }
        return urllib.urlencode(params)

    @property
    def access_token_url(self):
        return self._OAUTH_ACCESS_TOKEN_URL
        return url_concat(self._OAUTH_ACCESS_TOKEN_URL, params)

    def on_access_token(self, response):
        if response.code != 200:
            self.write('<p>Something is wrong</p>')
        else:
            self.write('<p>Ok!</p>')

        self.write('<p>Response body: {0}</p>'.format(response.body))
        self.finish()



urls = (
    (r'/', Home),
    (r'/return', Return),
)
application = Application(urls, debug=True)

if __name__ == '__main__':
    port = 8000
    application.listen(port)
    print("Listening on {0}".format(port))
    IOLoop.instance().start()
