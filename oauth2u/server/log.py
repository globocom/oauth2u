import logging

def configure(**kwargs):
    logging.basicConfig(**kwargs)


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
