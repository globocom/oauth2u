# OAuth 2 server and client implementation

This project aims to implement the complete
[OAuth 2.0 Authorization Protocol Specification](http://tools.ietf.org/html/draft-ietf-oauth-v2-22).


# Server

The first part is a oauth 2.0 server. It provides the endpoints specified
by oauth 2.0 specification with possibilities to plug code to customize
specific behaviours (see plugins bellow).
You can also extend the server adding additional urls.

Here is an example on how to start the server:

    from oauth2u.server import Server

    server = Server(port=8080)
    server.start()

**Available parameters**

- `port`: specify which port the server will listen (default is 8000)
- `plugins_directories`: a list of absolute directories the server executes to register
   plugins
- `handlers_directories`: a list of absolute directories the server executes to register
   new urls handlers

There is a server on tests/servertest.py.

## Extending the Server

There are two possible ways to extend the server: new urls and plugins

### Plugins

With plugins is possible to customize specific behaviours from the server.
It's similar to a Template Method pattern, but doesn't require you to extend
(or even know) the class that calls it.

You cannot create new plugins, unless you want to call them yourself. But
there are some pre-defined plugins called on specific parts of the server.

To let the server load your plugins automatically you can provide
a list of directories to `Server()` parameter: `plugins_directories`.

##### `authorization_GET`

- __Parameters__
 - `handler`: tornado Request Handler reference

Is called on the Authorization Request handler GET HTTP method, after all
validations are made and the authorization code has already been generated
and saved on database.

If no plugin is registered here the server redirects to `redirect_uri`
without any specific verification.

There is an example usage on how to build a login window using this plugin
and `authorization-POST` on [examples folder](https://github.com/globocom/oauth2u/blob/master/examples/server_with_plugin_to_login.py)

##### `authorization_POST`

- __Parameters__
 - `handler`: tornado Request Handler reference

Is called on the Authorization Request handler POST HTTP method. There is
not default behaviour, if no plugins is registered a `405` status code response is
generated

##### `access_token_response`

- __Parameters__
 - `handler`: tornado Request Handler reference
 - `response`: the default dict to build the json response, with keys: `access_token`,
    `token_type` and `expires_in`

Is called in the end of Access Token request handler, when the json is about to be
written in the HTTP response.
The plugin callback can edit the response dict adding, removing or editing keys.
Just be careful to don't remove [required OAuth 2.0 parameters](http://tools.ietf.org/html/draft-ietf-oauth-v2-22#section-4.1.4)

Example:

        @plugins.access_token_response
        def customize_response(handler, response):
            response.pop('expires_in')   # it's optional, and I don't want it...
            response['user_name'] = 'Bob'


### New urls handlers

Since the server is written using [tornado web framework](http://tornadoweb.org), is
natural that you can register new handlers.

Example:

        import tornado
        from oauth2u.server import handlers

        @handlers.register('/my/custom/url')
        class DummyHandler(tornado.web.RequestHandler):
            def get(self):
                self.write("hello world")

Read the tornado docs for more information on Request Handlers

To let the server load your new url handlers automatically you can provide
a list of directories to `Server()` parameter: `handlers_directories`.

# How to contribute

- Create a fork on github: https://github.com/globocom/oauth2u

- Install the package for development (preferably
  using [virtualenv](http://pypi.python.org/pypi/virtualenv)):

   `$ pip install -e oauth2u`

- Run tests (this command will install test specific dependencies):

   `$ ./runtests`

- Open an [issue](https://github.com/globocom/oauth2u/issues),
  if it doesn't exist yet, assign it to you and commit your changes
  in your fork.

- Send a pull request

- Your commits must have tests, we have 100% coverage, so any code without
  tests is aren't welcome :).
  If your changes modifies API or adds a new feature, you must update the docs too
