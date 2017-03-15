# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

import logging
import os
import sys

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

__authors__ = "Shanming Liu"


class LoggerAttributeError(AttributeError):
    pass


class LogCacheManagerException(Exception):
    pass


class LogCache(object):
    def __init__(self, writer):
        self.log_write = writer
        self.cache = ''
        super(LogCache, self).__init__()

    def write(self, data):
        self.cache += data
        # if '\n' in self.cache or '\r' in self.cache or len(self.cache) > 100:
        #     self.output()
        self.output()

    def output(self):
        if self.cache:
            self.log_write(self.cache.strip('\r\n'))
            self.cache = ''

    def flush(self):
        self.output()


class LogCacheManager(object):
    ATTR = ('CRITICAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG')

    def __init__(self, logger):
        self.logger = logger
        self.caches = dict()
        super(LogCacheManager, self).__init__()

    def register(self, log_type):
        if log_type.upper() not in self.ATTR:
            raise LogCacheManagerException('Not support {} yet'.format(log_type))

        self.caches[log_type.upper()] = LogCache(getattr(self.logger, log_type.lower()))

    def unregister(self, log_type):
        log_upper = self._check_log_type(log_type)
        del self.caches[log_upper]

    def get_cache(self, log_type):
        return self.caches[self._check_log_type(log_type)]

    def _check_log_type(self, log_type):
        log_upper = log_type.upper()
        if log_upper not in self.ATTR:
            raise LogCacheManagerException('Not support {} yet'.format(log_type))

        if log_upper not in self.caches:
            raise LogCacheManagerException('No cache log {}'.format(log_type))

        return log_upper

    def flush(self):
        for cache in self.caches.values():
            cache.flush()


class Logger(object):
    def __init__(self, name, level=logging.INFO, console=True, file_path=None):
        self.name = name
        self.level = level
        self.logger_formatter = logging.Formatter(fmt='%(asctime)s [%(levelname)-5s] %(message)s')
        self.console = console

        self.logger = None
        self.cache_manager = None
        self._init_logger()

        # self.register_caches()
        # self.partial_attribute()

        if console:
            self.enable_console_handle()

        if file_path:
            self.enable_log_file_handle(file_path)

    def register_caches(self):
        for log_type in self.cache_manager.ATTR:
            self.cache_manager.register(log_type)

    def partial_attribute(self):
        for log_type in self.cache_manager.ATTR:
            setattr(self, log_type.lower(), self.cache_manager.get_cache(log_type).write)

    def _init_logger(self):
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(self.level)

        self.cache_manager = LogCacheManager(self.logger)

    def enable_console_handle(self, formatter=None):
        console_handle = logging.StreamHandler(stream=sys.stdout)
        console_handle.setFormatter(self.get_log_formatter(formatter))
        self.logger.addHandler(console_handle)

    def enable_log_file_handle(self, filename, mode='w', formatter=None):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError:
            pass

        file_handle = logging.FileHandler(filename, mode=mode)
        file_handle.setFormatter(self.get_log_formatter(formatter))
        self.logger.addHandler(file_handle)

    def get_log_formatter(self, formatter):
        return self.logger_formatter if formatter is None else formatter

    def get_child(self, suffix, level=logging.DEBUG, console=False, file_path=None):
        if self.logger.root is not self.logger:
            suffix = '.'.join((self.name, suffix))

            return Logger(suffix, level=level, console=console, file_path=file_path)

    def __getattr__(self, item):
        try:
            return getattr(self.logger, item)
        except AttributeError:
            raise LoggerAttributeError("No Attribute name of {}".format(str(item)))

    def flush(self):
        # self.cache_manager.flush()
        for handle in self.logger.handlers:
            handle.flush()


if __name__ == '__main__':
    logger1 = Logger('aaaa', level='DEBUG', file_path='test1.log')
    logger2 = logger1.get_child('bbb', file_path='test2.log')
    # logger2.addHandler(console_handle)

    logger1.debug('aa')
    logger2.info('bb')
    # logger1.flush()
    # logger2.flush()
