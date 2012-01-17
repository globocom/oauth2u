
from oauth2u.server import plugins

@plugins.register('authorization-POST')
def on_authorization_POST_do_nothing(handler):
    handler.write('do nothing')
    
