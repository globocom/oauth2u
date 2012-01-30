'''
These plugins are registered to test non-default but possible
behaviours of the server.

And also to test if plugins registration really works. Every test
that relies on a plugin has a comment about it

The plugin handler knows which test is running at the moment
based on ``client_id`` parameter. Each test that uses plugins
informs a specific ``client_id``.

'''

from oauth2u.server import plugins

@plugins.authorization_GET
def on_authorization_GET_to_test(handler):
    if handler.client_id == 'unauthorized-client':
        handler.redirect_unauthorized_client(handler.client_id, handler.code)
        return
    if handler.client_id == 'temporarily_unavailable':
        handler.redirect_temporarily_unavailable(handler.client_id, handler.code)
        return
    if handler.client_id == 'server_error':
        handler.redirect_server_error(handler.client_id, handler.code)
        return
    if handler.client_id == 'invalid_scope':
        handler.redirect_invalid_scope(handler.client_id, handler.code)
        return

    handler.set_cookie('client_id', handler.client_id)
    handler.set_cookie('code', handler.code)

    if handler.client_id == 'client-id-from-plugins-test':
        handler.write("I'm a dummy plugin doing nothing on GET")

    elif handler.client_id == 'client-id-verify-access':
        handler.write('Hello resource owner, do you allow this client to access your resources?')

    else:
        # keep normal if no special client_id, so other tests
        # can check default behaviour
        from oauth2u.server import plugins
        raise plugins.IgnorePlugin()


@plugins.authorization_POST
def on_authorization_POST_to_test(handler):
    client_id = handler.get_cookie('client_id')
    code = handler.get_cookie('code')

    if client_id == 'client-id-from-plugins-test':
        handler.write("I'm a dummy plugin doing nothing on POST")

    elif client_id == 'client-id-verify-access':
        if handler.get_argument('allow') == 'yes':
            handler.redirect_access_granted(client_id, code)
        else:
            handler.redirect_access_denied(client_id, code)
    else:
        # keep normal if no special client_id, so other tests
        # can check default behaviour
        from oauth2u.server import plugins
        raise plugins.IgnorePlugin()


@plugins.access_token_response
def on_access_token_response(handler, response):
    if handler.client_id == 'client-id-from-access-token-tests':
        response['user_name'] = 'Igor Sobreira'

@plugins.access_token_validation
def on_access_token_validation(handler):
    if handler.client_id == 'rejected-client-id':
        handler.raise_http_400({'error': 'invalid_request',
                                'error_description': 'My plugin rejected your request'})
