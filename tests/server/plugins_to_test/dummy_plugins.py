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

@plugins.register('authorization-GET')
def on_authorization_GET_to_test(handler):
    handler.set_cookie('client_id', handler.client_id)
    handler.set_cookie('code', handler.code)

    if handler.client_id == 'client-id-from-plugins-test':
        # in this case i'm being tested by the plugins tests
        # so i just override the default execution
        handler.write("I'm a dummy plugin doing nothing on GET")
    elif handler.client_id == 'client-id-access-denied':
        handler.write('Hello resource owner, do you allow this client to access your resources?')
    else:
        # otherwise, keep normal execution so the other
        # tests don't break
        from oauth2u.server import plugins
        raise plugins.IgnorePlugin()


@plugins.register('authorization-POST')
def on_authorization_POST_to_test(handler):
    # TODO: get from cookie
    client_id = handler.get_argument('client_id', 'CLIENT_ID-NOT-INFORMED')

    if client_id == 'client-id-from-plugins-test':
        # in this case i'm being tested by the plugins tests
        # so i just override the default execution
        handler.write("I'm a dummy plugin doing nothing on POST")
    elif client_id == 'client-id-access-denied':
        code = handler.get_cookie('code')
        if handler.get_argument('allow') == 'no':
            handler.redirect_access_denied(client_id, code)
    else:
        # otherwise, keep normal execution so the other
        # tests don't break
        from oauth2u.server import plugins
        raise plugins.IgnorePlugin()


@plugins.register('access-token-response')
def on_access_token_response(handler, response):
    if handler.client_id == 'client-id-from-access-token-tests':
        response['user_name'] = 'Igor Sobreira'
