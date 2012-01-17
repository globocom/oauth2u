import os
from oauth2u.server import loader

__all__ = 'register', 'items', 'unregister_all', 'load_from_directories'

URLS = {}

def register(url):
    def decorator(klass):
        URLS[url] = klass
        return klass
    return decorator


def items():
    return URLS.iteritems()


def unregister_all():
    URLS.clear()


def load_from_directories(*directory_list):
    loader.load_from_directories(*directory_list)
