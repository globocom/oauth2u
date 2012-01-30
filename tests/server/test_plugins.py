import os.path

import requests
import pytest

from oauth2u.server import plugins
from tests.helpers import build_authorize_url

def setup_function(funct):
    plugins.unregister_all()

def teardown_function(func):
    plugins.unregister_all()


def test_should_register_plugins():
    assert_no_plugin_for('authorization-GET')

    @plugins.authorization_GET
    def on_authorization_GET(handler):
        handler.write('do nothing')

    assert_plugin_is('authorization-GET', on_authorization_GET)


def test_should_raise_InvalidPlugin_if_trying_to_register_on_non_existent_plugin_name():
    with pytest.raises(plugins.InvalidPlugin) as error:
        @plugins.register('NON-EXISTENT-PLUGIN')
        def on_authorization_GET(handler):
            handler.write('do nothing')

    assert "Plugin name 'NON-EXISTENT-PLUGIN' is invalid" in str(error)


def test_should_override_existing_plugin_if_new_register():
    @plugins.authorization_GET
    def on_authorization_GET(handler):
        handler.write('do nothing')

    @plugins.authorization_GET
    def new_on_authorization_GET(handler):
        handler.write('no a bit more...')

    assert_plugin_is('authorization-GET', new_on_authorization_GET)


def test_should_find_plugin_by_name():
    @plugins.authorization_GET
    def on_authorization_GET(handler):
        handler.write('do nothing')

    assert on_authorization_GET == plugins.find('authorization-GET')


def test_should_raise_PluginNotFound_if_trying_to_find_plugin_but_none_registered():
    with pytest.raises(plugins.PluginNotFound) as error:
        plugins.find('authorization-POST')

    assert "No plugin registered to 'authorization-POST'" in str(error)


def test_should_raise_InvalidPlugin_if_trying_to_find_plugin_on_invalid_plugin_name():
    with pytest.raises(plugins.InvalidPlugin) as error:
        plugins.find('NO-SUCH-PLUGIN-NAME')

        assert "Plugin name 'NO-SUCH-PLUGIN-NAME' is invalid. So it's not possible to look for plugins with this name" in str(error)


def test_should_load_plugins_from_directories():
    directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'plugins_to_test'))

    assert_no_plugin_for('authorization-POST')
    plugins.load_from_directories(directory)

    function = plugins.find('authorization-POST')

    assert 'on_authorization_POST_to_test' == function.__name__

def test_call_should_return_False_if_plugin_not_found():
    assert plugins.call('authorization-GET') is False


def test_call_should_let_InvalidPlugin_exception_to_be_raised():
    with pytest.raises(plugins.InvalidPlugin):
        plugins.call('INVALID-PLUGIN')


def test_call_should_return_True_if_plugin_called():
    called = []
    @plugins.authorization_GET
    def on_authorization_GET(handler):
        called.append(handler)

    assert plugins.call('authorization-GET', "handler") is True
    assert ["handler"] == called


def test_call_should_return_False_if_plugin_raises_IgnorePlugin():
    called = []
    @plugins.authorization_GET
    def on_authorization_GET(handler):
        called.append(handler)
        raise plugins.IgnorePlugin()

    assert plugins.call('authorization-GET', "handler") is False
    assert ["handler"] == called


# custom asserts

def assert_no_plugin_for(plugin_name):
    assert plugins.PLUGINS[plugin_name] is None

def assert_plugin_is(plugin_name, function):
    assert function == plugins.PLUGINS[plugin_name]
