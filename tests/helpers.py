import sys
import urllib
from functools import partial

TEST_SERVER_HOST = 'http://localhost:8888'

def build_url(host, path, query=None):
    query = query or {}
    return u'{0}/{1}?{2}'.format(host.rstrip('/'),
                                 path.lstrip('/'),
                                 urllib.urlencode(query))

build_root_url = partial(build_url, TEST_SERVER_HOST)

build_authorize_url = partial(build_url, TEST_SERVER_HOST, '/authorize')
build_access_token_url = partial(build_url, TEST_SERVER_HOST, '/access-token')
