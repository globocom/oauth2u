import mock

from oauth2u.server import log


def test_configure_should_call_basicConfig_on_logging_with_default_parameters(monkeypatch):
    logging_mock = mock.Mock()
    monkeypatch.setattr(log, 'logging', logging_mock)

    log.configure(filename='/tmp/log')

    assert 1 == logging_mock.basicConfig.call_count
    logging_mock.basicConfig.assert_called_with(filename='/tmp/log',
                                                level=log.DEFAULT_LEVEL,
                                                format=log.DEFAULT_FORMAT)


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
