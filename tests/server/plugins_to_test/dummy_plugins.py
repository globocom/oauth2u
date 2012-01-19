
from oauth2u.server import plugins

@plugins.register('authorization-GET')
def on_authorization_GET_to_test(handler):
    if handler.client_id == 'client-id-from-plugins-test':
        # in this case i'm being tested by the plugins tests
        # so i just override the default execution
        handler.write("I'm a dummy plugin doing nothing on GET")
    else:
        # otherwise, keep normal execution so the other
        # tests don't break
        from oauth2u.server import plugins
        raise plugins.IgnorePlugin()


@plugins.register('authorization-POST')
def on_authorization_POST_to_test(handler):
    client_id = handler.get_argument('client_id', 'CLIENT_ID-NOT-INFORMED')
    if client_id == 'client-id-from-plugins-test':
        # in this case i'm being tested by the plugins tests
        # so i just override the default execution
        handler.write("I'm a dummy plugin doing nothing on POST")
    else:
        # otherwise, keep normal execution so the other
        # tests don't break
        from oauth2u.server import plugins
        raise plugins.IgnorePlugin()


@plugins.register('access-token-response')
def on_access_token_response(handler, response):
    if handler.client_id == 'client-id-from-access-token-tests':
        response['user_name'] = 'Igor Sobreira'
