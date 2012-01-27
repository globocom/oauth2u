import logging
from logging.handlers import TimedRotatingFileHandler

DEFAULT_LEVEL = logging.INFO
DEFAULT_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
DEFAULT_DATEFMT = '%Y-%m-%d %H:%M'

def configure(**kwargs):
    '''
    Configure python default logger.

    Logs to stderr by default. It's possible to customize
    passing names parameters, same as `logging.basicConfig()'.

    If you provide a `filename' parameter, a
    `TimedRotatingFileHandler' will be configured instead of
    `logging.basicConfig()'.

    '''
    defaults = {
        'level': DEFAULT_LEVEL,
        'format': DEFAULT_FORMAT,
        'datefmt': '%Y-%m-%d %H:%M',
        }
    defaults.update(kwargs)

    if 'filename' in defaults:
        _configure_with_rotate(defaults)
    else:
        _basic_configuration(defaults)

def critical(msg, *args, **kwargs):
    logging.critical(msg, *args, **kwargs)

def error(msg, *args, **kwargs):
    logging.error(msg, *args, **kwargs)

def exception(msg, *args):
    logging.exception(msg, *args)

def warn(msg, *args, **kwargs):
    logging.warn(msg, *args, **kwargs)

def info(msg, *args, **kwargs):
    logging.info(msg, *args, **kwargs)

def debug(msg, *args, **kwargs):
    logging.debug(msg, *args, **kwargs)


def _configure_with_rotate(options):
    formatter = logging.Formatter(options['format'])

    handler = TimedRotatingFileHandler(options['filename'],
                                       when=options.get('when', 'midnight'),
                                       encoding=options.get('encoding', 'utf-8'),
                                       interval=options.get('interval', 1))
    handler.setLevel(options['level'])
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(options['level'])

def _basic_configuration(options):
    logging.basicConfig(**options)
