# OAuth 2 server and client implementation

The idea is to implement an extensible server and a client of 
the [OAuth 2.0 Authorization Protocol](http://tools.ietf.org/html/draft-ietf-oauth-v2-22).


## How to contribue

1. Create a fork on github: https://github.com/igorsobreira/oauth2u

2. Install the package for development:

   `$ pip install -e oauth2u`

3. Run tests:

   `$ ./runtests`

4. Open an [issue](https://github.com/igorsobreira/oauth2u/issues),
   if it doesn't exist yet, assign it to you and commit your changes 
   in your fork. 

5. Send a pull request


## Extending the Server

There are two possible ways to extend the server: new urls and plugins

### Plugins

With plugins is possible to customize specific behaviours from the server.
It's similar to a Template Method pattern, but doesn't require you to extend
(or even know) the class that calls it.

You cannot create new plugins, unless you want to call them yourself. But
there are some pre-defined plugins called on specific parts of the server.

#### Using

TODO

##### `authorization-GET`

- __Parameters__
 - `handler`: tornado Request Handler reference

Is called on the Authorization Request handler GET HTTP method, after all 
validations are made and the authorization code has already been generated
and saved on database.

If no plugin is registered here the server redirects to `redirect_uri`
without any specific verification.

There is an example usage on how to build a login windown using this plugin
and `authorization-POST` on [examples folder](https://github.com/igorsobreira/oauth2u/blob/master/examples/server_with_plugin_to_login.py)

##### `authorization-POST`

- __Parameters__
 - `handler`: tornado Request Handler reference

Is called on the Authorization Request handler POST HTTP method. There is 
not default behaviour, if no plugins is registered a `405` status code response is
generated

##### `access-token-response`

- __Parameters__
 - `handler`: tornado Request Handler reference
 - `response`: the default dict to build the json response, with keys: `access_token`,
    `token_type` and `expires_in`

Is called in the end of Access Token request handler, when the json is about to be
written in the HTTP response.
The plugin callback can edit the response dict adding, removing or editing keys.
Just be careful to don't remove [required OAuth 2.0 parameters](http://tools.ietf.org/html/draft-ietf-oauth-v2-22#section-4.1.4)

Example:
        
        @plugins.register('access-token-response')
        def customize_response(handler, response):
            response.pop('expires_in')   # it's optional, and I don't want it...
            response['user_name'] = 'Bob'


### New urls handlers

Since the server is written using (tornado web framework)[http://tornadoweb.org], is
natural that you can register new handlers.

Example:

        import tornado
        from oauth2u.server import handlers

        @handlers.register('/my/custom/url')
        class DummyHandler(tornado.web.RequestHandler):
            def get(self):
                self.write("hello world")

Read the tornado docs for more information on Request Handlers