import os.path

import pytest
import requests
import tornado

from oauth2u.server import handlers
from tests.helpers import build_root_url


def setup_function(func):
    handlers.unregister_all()

def teardown_function(func):
    handlers.unregister_all()


def test_should_register_new_url_handler():
    assert_no_url_handler_for('/test/dummy-url')

    @handlers.register(r'/test/dummy-url')
    class DummyHandler(tornado.web.RequestHandler):
        def get(self):
            self.write("Dummy handler")

    assert_url_handler('/test/dummy-url', DummyHandler)


def test_should_load_handlers_from_directories():
    directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'handlers_to_test'))

    assert_no_url_handler_for('/test/dummy-url')
    handlers.load_from_directories(directory)
    assert_url_handler_name('/test/dummy-url', 'DummyHandler')


def test_items_should_list_all_urls_and_handlers():
    @handlers.register(r'/test/dummy-url')
    class DummyHandler(tornado.web.RequestHandler):
        def get(self):
            self.write("Dummy handler")

    assert [('/test/dummy-url', DummyHandler)] == list(handlers.items())


def test_registered_handler_should_work_as_a_normal_url_handler():
    @handlers.register(r'/test/dummy-url')
    class DummyHandler(tornado.web.RequestHandler):
        def get(self):
            self.write("Dummy handler")
    
    resp = requests.get(build_root_url('/test/dummy-url'))

    assert 200 == resp.status_code
    assert "Dummy handler" == resp.content


@pytest.mark.xfail
def test_should_return_405_for_not_implemented_methods_on_default_handlers():
    assert 0


def test_add_query_to_url_should_add_more_query_params_to_url():
    url = 'http://www.example.com/path?name=value'
    params = {'foo': 'bar'}

    result = handlers.add_query_to_url(url, params)
    assert 'http://www.example.com/path?foo=bar&name=value' == result


def test_should_return_500_for_error():
    resp = requests.get(build_root_url('/test/faulty-url'))
    assert 500 == resp.status_code


# custom asserts

def assert_no_url_handler_for(url):
    assert dict(handlers.items()).get(url) is None

def assert_url_handler(url, handler):
    assert dict(handlers.items()).get(url) is handler

def assert_url_handler_name(url, handler_name):
    assert dict(handlers.items())[url].__name__ == handler_name
