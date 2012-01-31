import tornado

class BaseRequestHandler(tornado.web.RequestHandler):

    def require_argument(self, name, expected_value=None):
        value = self.get_argument(name, None)
        self.validate_argument(name, value, expected_value)
        return value

    def validate_argument(self, name, value, expected_value):
        if value is None:
            error_description = u'Parameter {0} is required'.format(name)
        elif expected_value and value != expected_value:
            error_description = u'Parameter {0} should be {1}'.format(name, expected_value)
        else:
            return

        error = {'error': 'invalid_request',
                 'error_description': error_description}

        self.raise_http_invalid_argument_error(name, error)

    def raise_http_invalid_argument_error(self, parameter, error):
        self.raise_http_400(error)

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

    def raise_http_302(self, query_parameters):
        headers = {'Location': self.build_redirect_uri(query_parameters)}
        self.raise_http_error(302, headers=headers)

    def raise_http_400(self, response_body):
        self.raise_http_error(400, response_body)

    def raise_http_401(self, response_body):
        self.raise_http_error(401, response_body,
                              {'WWW-Authenticate': 'Basic realm="OAuth 2.0 Secure Area"'})

    def raise_http_error(self, status, response_body=None, headers=None):
        error = tornado.web.HTTPError(status, '')
        error.response_body = response_body
        error.headers = headers or {}
        raise error

    def get_error_html(self, status_code, **kwargs):
        ''' Called by tornado to fill error response body '''
        exception = kwargs.pop('exception', None)
        if hasattr(exception, 'response_body') and exception.response_body:
            self.write(exception.response_body)

        if hasattr(exception, 'headers'):
            for name, value in exception.headers.items():
                self.set_header(name, value)
