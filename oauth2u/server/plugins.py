import functools
import os

import tornado

from oauth2u.server import database, loader


PLUGINS = {
    'authorization-GET': None,
    'authorization-POST': None,
    'access-token-response': None,
    'access-token-validation': None,
}

def register(name):
    def decorator(function):
        if name not in PLUGINS:
            raise InvalidPlugin("Plugin name '{0}' is invalid".format(name))
        PLUGINS[name] = function
        return function
    return decorator

authorization_GET = register('authorization-GET')
authorization_POST = register('authorization-POST')
access_token_response = register('access-token-response')
access_token_validation = register('access-token-validation')

def find(name):
    if name not in PLUGINS:
        raise InvalidPlugin("Plugin name '{0}' is invalid. So it's not possible to look for plugins with this name".format(name))
    function = PLUGINS.get(name)
    if not function:
        raise PluginNotFound("No plugin registered to '{0}'".format(name))
    return function


def call(name, *args, **kwargs):
    try:
        function = find(name)
    except PluginNotFound:
        return False
    try:
        function(*args, **kwargs)
    except IgnorePlugin:
        return False
    return True


def unregister_all():
    for key in PLUGINS:
        PLUGINS[key] = None


def load_from_directories(*directory_list):
    loader.load_from_directories(*directory_list)


class PluginNotFound(Exception):
    pass

class InvalidPlugin(Exception):
    pass

class IgnorePlugin(Exception):
    pass
