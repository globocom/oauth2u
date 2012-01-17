import os
from oauth2u.server import loader

URLS = {}

def register(url):
    def decorator(klass):
        URLS[url] = klass
        return klass
    return decorator


def unregister_all():
    URLS.clear()


def load_from_directories(*directory_list):
    loader.load_from_directories(*directory_list)
