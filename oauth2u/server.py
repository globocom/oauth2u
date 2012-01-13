import uuid

from tornado.web import RequestHandler, Application
from tornado.ioloop import IOLoop
from tornado.auth import OAuth2Mixin
from tornado.httputil import url_concat

class Authorize(RequestHandler):

    def get(self):
        self.write('<h1>Credentials</h1>')
        self.write('<form method="post" action="'+ self.request.full_url() +'">')
        self.write('<p>Login: <input name="username" type="text" /></p>')
        self.write('<p>Password: <input name="password" type="password" /></p>')
        self.write('<p><button type="submit">Send</button></p>')
        self.write('</form>')

    def post(self):
        client_id = self.get_argument('client_id')

        if self.valid_user():
            code = self.build_token()
            self.redirect_with_code(code)
        else:
            self.write("Invalid username and/or password")
            
    def valid_user(self):
        return True

    def build_token(self):
        return str(uuid.uuid4())

    def redirect_with_code(self, code):
        url = self.build_redirect_url(code)
        self.redirect(url)

    def build_redirect_url(self, code):
        redirect_uri = self.get_argument('redirect_uri')
        return url_concat(redirect_uri, {'code': code})

class AccessToken(RequestHandler):

    def post(self):
        import time
        time.sleep(2)
        if self.is_valid_code_for_client():
            self.return_access_token()
    
    def is_valid_code_for_client(self):
        # verify if the client registered for this redirect uri
        # should be using this code
        grant_type = self.get_argument('grant_type')
        code = self.get_argument('code')
        redirect_uri = self.get_argument('redirect_uri')
        return True

    def return_access_token(self):
        response = self.build_token()
        self.write(response)

    def build_token(self):
        return {
            'access_token': str(uuid.uuid4()),
            'refresh_token': str(uuid.uuid4()),
            'expires_in': 3600,
            }

urls = (
    (r'/authorize', Authorize),
    (r'/access-token', AccessToken),
)
application = Application(urls, debug=True)


if __name__ == '__main__':
    port = 8008
    application.listen(port)
    print("Listening on {0}".format(port))
    IOLoop.instance().start()
