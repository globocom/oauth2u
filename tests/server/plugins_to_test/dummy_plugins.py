
from oauth2u.server import plugins

@plugins.register('authorization-POST')
def on_authorization_POST_do_nothing(handler):
    handler.write('do nothing')

@plugins.register('authorization-GET')
def on_authorization_GET(handler):
    if handler.client_id == 'client-id-from-plugins-test':
        # in this case i'm being tested by the plugins tests
        # so i just override the default execution
        handler.write("I'm a dummy plugin doing nothing")
    else:
        # otherwise, keep normal execution so the other
        # tests don't break
        from oauth2u.server import plugins
        raise plugins.IgnorePlugin()

    
