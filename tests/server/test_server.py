import logging

import mock

import oauth2u
import oauth2u.server.log

def teardown_function(func):
    logging.disable(logging.INFO)

def test_should_have_optional_port():
    server = oauth2u.Server()
    assert 8000 == server.port


def test_should_accept_custom_port():
    server = oauth2u.Server(8888)
    assert 8888 == server.port


def test_should_configure_log_with_default_configurations(monkeypatch):
    log_mock = mock.Mock()
    monkeypatch.setattr(oauth2u.server, 'log', log_mock)

    server = oauth2u.Server()

    assert 1 == log_mock.configure.call_count
    log_mock.configure.assert_called_with()


def test_should_override_default_log_parameters(monkeypatch):
    log_mock = mock.Mock()
    monkeypatch.setattr(oauth2u.server, 'log', log_mock)

    server = oauth2u.Server(log_config={'format': '%(message)s'})

    assert 1 == log_mock.configure.call_count
    log_mock.configure.assert_called_with(format='%(message)s')
