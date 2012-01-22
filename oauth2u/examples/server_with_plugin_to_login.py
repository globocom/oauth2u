'''
This example shows how to use a plugin to ask for client
login and password.

If you have an application/website with registered users, you
can allow any application to authenticate using oauth 2 protocol
implementing plugins like these bellow

'''

from oauth2u.server import Server, plugins, database

@plugins.register('authorization-GET')
def ask_user_credentials(handler):
    '''
    This plugin will execute in the end of the authorization request.
    All validation will already be executed.
    
    ``handler`` is the tornado's RequestHandler instance. It's possible to
    fetch the client_id in ``handler.client_id``.

    Note that the tokens have already been generated and stored on 
    ``oauth2u.server.database``. You'll need the client id to query.

    '''
    # Stores the client_id in a session to be able to access from the
    # authorization-POST plugin. That is because in POST nothing is executed
    # in the default handler, so we need to query the tokens generated on GET
    # using the client_id
    handler.set_secure_cookie('client_id', handler.client_id)
    handler.set_secure_cookie('code', handler.code)

    # show the login form
    handler.write('<h1>Inform your username and password</h1>'
                  '<form method="post">'
                  '<p> Username: <input type="text" name="username" /> </p>'
                  '<p> Password: <input type="password" name="password" /> </p>'
                  '<p>The application {0} wants to access your information, do you allow?</p>'
                  '<p> Yes, I do <input type="checkbox" name="allow" /> </p>'
                  '<button type="submit">Allow</button>'.format(handler.client_id))


@plugins.register('authorization-POST')
def validate_user_credentials(handler):
    '''
    This plugin will execute in the authorization request handler, but on POST
    method.

    Different from GET method, no code is executed in the default handler. So
    why we use ``client_id`` (stored on cookie by ``ask_user_credentials() above``)
    to query tokens from database (saved on GET handler)

    '''
    client_id = handler.get_secure_cookie('client_id')
    code = handler.get_secure_cookie('code')

    credentials = (handler.get_argument('username',''),
                   handler.get_argument('password',''))

    allow = (handler.get_argument('allow','off') == 'on')

    if not database.client_has_authorization_code(client_id, code):
        handler.write('<p>No authorization code created to this client_id</p>')
    elif credentials == ('admin', 'admin'):
        if allow:
            handler.redirect_access_granted(client_id, code)
        else:
            handler.redirect_access_denied(client_id, code)
    else:
        handler.write('<p>Invalid username and/or password</p>'
                      '<p><em>hint: try "admin" and "admin"</em></p>'
                      '<p><a href="{0}">Try again</a></p>'.format(handler.request.uri))


if __name__ == '__main__':
    PORT = 8888

    s = Server(port=PORT)
    print '\n => Listening on ' + str(PORT)
    print '  - Authorization request endpoint: http://localhost:{0}/authorize'.format(PORT)
    print '  - Access token request endpoing: http://localhost:{0}/access-token'.format(PORT)
    s.start()
