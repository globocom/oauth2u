# coding: utf-8
from __future__ import absolute_import

import os
import os.path
import logging
from logging.handlers import TimedRotatingFileHandler

class Log(object):
    proxy_methods = ('info', 'debug', 'error', 'warning', 'critical', 'exception')

    def __init__(self):
        self.logging = logging

    def configure(self):
        self.logging.getLogger().addHandler(self._handler)
        self.logging.getLogger().setLevel(self._level)

    def __getattr__(self, name):
        if name in self.proxy_methods:
            return getattr(self.logging, name)
        raise AttributeError('%r object has no attribute %r' % (self, name))

    @property
    def _handler(self):
        handler = TimedRotatingFileHandler(self._filename,
                                           when='midnight',
                                           encoding='utf-8')
        handler.setLevel(self._level)
        handler.setFormatter(self._format)
        return handler

    @property
    def _filename(self):
        return os.environ.get('OAUTH2U_LOG_PATH', '/tmp')

    @property
    def _format(self):
        return logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
    
    @property
    def _level(self):
        return os.environ.get('OAUTH2U_LOG_LEVEL', 'debug').upper()


# normalmente dentro do projeto usa-se essa instância para logar.
# a não ser que alguma classe herde de LogMixin 
log = Log()

class LogMixin(object):
    '''
    Essa classe eh usada como mixin para que, dentro dos 
    métodos de uma classe, ao usar self.log.debug() a mensagem
    sempre informe o nome da classe. Ex.:

    class MyClass(MyBaseClass, LogMixin):

       def do_something(self):
          self.log.info("Ops")

    resulta no log em:

    [MyClass] Ops

    '''
    def __init__(self):
        prefix = self.__class__.__name__
        self.log = PrefixedLog(prefix, log)

class PrefixedLog(object):
    '''
    Essa é uma classe auxiliar que encapsula todas as chamadas
    ao ``log``, para adicionar um prefixo ``prefix`` nas mensagens.

    É utilizada pela ``LogMixin``

    '''
    def __init__(self, prefix, log):
        self.prefix = prefix
        self.log = log

    def __getattr__(self, name):
        prefix = self.prefix

        def prefixed_log(method):
            def log(msg, *args, **kw):
                msg = u'[%s] %s' % (prefix, msg)
                return method(msg, *args, **kw)
            return log

        if name in log.proxy_methods:
            return prefixed_log(getattr(log, name))

        raise AttributeError('%r object has no attribute %r' % (self, name))
