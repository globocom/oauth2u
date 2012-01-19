import tornado

class BaseRequestHandler(tornado.web.RequestHandler):

    def require_argument(self, name, expected_value=None):
        value = self.get_argument(name, None)
        if value is None:
            self.raise_http_400({'error': 'invalid_request',
                                 'error_description': u'Parameter {0} is required'.format(name)})

        if expected_value and value != expected_value:
            self.raise_http_400({'error': 'invalid_request',
                                 'error_description': u'Parameter {0} should be {1}'.format(name, expected_value)})
        return value

    def require_header(self, name, expected_value=None, startswith=None):
        value = self.request.headers.get(name)
        if value is None:
            self.raise_http_400({'error': 'invalid_request',
                                 'error_description': u'Header {0} is required'.format(name)})

        if expected_value and value != expected_value:
            self.raise_http_400({'error': 'invalid_request',
                                 'error_description': u'Header {0} should be {1}'.format(name, expected_value)})

        if startswith and not value.startswith(startswith):
            self.raise_http_400({'error': 'invalid_request',
                                 'error_description': u'Header {0} should start with "{1}"'.format(name, startswith)})

        return value

    def raise_http_400(self, response_body):
        self.raise_http_error(400, response_body)

    def raise_http_401(self, response_body):
        self.raise_http_error(401, response_body,
                              {'WWW-Authenticate': 'Basic realm="OAuth 2.0 Secure Area"'})

    def raise_http_error(self, status, response_body, headers=None):
        error = tornado.web.HTTPError(status, '')
        error.response_body = response_body
        error.headers = headers or {}
        raise error

    def get_error_html(self, status_code, exception, **kwargs):
        ''' Called by tornado to fill error response body '''
        self.write(exception.response_body)

        for name, value in getattr(exception, 'headers', {}).items():
            self.set_header(name, value)

