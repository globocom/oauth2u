import logging
from logging.handlers import TimedRotatingFileHandler

import mock

from oauth2u.server import log

def setup_function(func):
    logging.root.handlers = []

def teardown_function(func):
    logging.root.handlers = []


def test_configure_should_call_basicConfig_on_logging_with_default_parameters(monkeypatch):
    logging_mock = mock.Mock()
    monkeypatch.setattr(log, 'logging', logging_mock)

    log.configure()

    assert 1 == logging_mock.basicConfig.call_count
    logging_mock.basicConfig.assert_called_with(level=log.DEFAULT_LEVEL,
                                                format=log.DEFAULT_FORMAT,
                                                datefmt=log.DEFAULT_DATEFMT)


def test_configure_should_use_time_rotating_file_handler_if_filename_provided(monkeypatch):
    log.configure(filename='/tmp/server.log')
    logger = log.logging.root

    assert log.DEFAULT_LEVEL == logger.level
    assert_time_rotating_file_handler(logger)
    assert_default_file_handler_configuration(logger.handlers[0],
                                              '/tmp/server.log')


def test_configure_should_override_default_time_rotating_file_handler_configuration():
    log.configure(filename='/tmp/server.log', when='S', interval=2, encoding='ascii',
                  level=logging.WARN)
    logger = log.logging.root

    assert logging.WARN == logger.level
    assert_time_rotating_file_handler(logger)

    handler = logger.handlers[0]

    assert 'S' == handler.when
    assert 2 == handler.interval
    assert 'ascii' == handler.encoding
    assert logging.WARN == handler.level

def test_log_functions_are_passed_to_logging_module(monkeypatch):
    logging_mock = mock.Mock()
    monkeypatch.setattr(log, 'logging', logging_mock)

    levels = ('critical', 'error', 'exception', 'warn', 'info', 'debug')

    for level in levels:
        function = getattr(log, level)
        function('logging a %s message', 'cool')

    for level in levels:
        function = getattr(logging_mock, level)
        assert 1 == function.call_count
        function.assert_called_with('logging a %s message', 'cool')


# custom asserts

def assert_time_rotating_file_handler(logger):
    assert 1 == len(logger.handlers)
    assert isinstance(logger.handlers[0], TimedRotatingFileHandler)

def assert_default_file_handler_configuration(handler, filename):
    assert 'MIDNIGHT' == handler.when
    assert filename == handler.baseFilename
    assert 'utf-8' == handler.encoding
    assert log.DEFAULT_LEVEL == handler.level
