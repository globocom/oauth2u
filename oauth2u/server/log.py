import logging

DEFAULT_LEVEL = logging.INFO
DEFAULT_FORMAT = '%(asctime)s:%(levelname)s:%(name)s: %(message)s'

def configure(**kwargs):
    defaults = {
        'level': DEFAULT_LEVEL,
        'format': DEFAULT_FORMAT,
        }
    defaults.update(kwargs)
    logging.basicConfig(**defaults)


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
