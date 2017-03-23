# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

import logging
import os
import sys
from decorator import decorator

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


@decorator
def log_strip(func, self, msg, *args, **kwargs):
    msg = msg.strip()
    if msg:
        func(self, msg, *args, **kwargs)


class Logger(object):
    FORMATTER = logging.Formatter(fmt='%(asctime)s <%(name)-5s> [%(levelname)-5s] %(message)s')

    def __init__(self, name=None, level=logging.INFO, console=True, filename=None):
        if name is None:
            self.name = 'runner'
        else:
            self.name = name
        self.level = level
        self.logger_formatter = None

        self._console = False
        self._filename = None

        self.logger = None
        self.cache_manager = None
        self._init_logger()

        self.console = console
        self.filename = filename

    def register_caches(self):
        for log_type in self.cache_manager.ATTR:
            self.cache_manager.register(log_type)

    def partial_attribute(self):
        for log_type in self.cache_manager.ATTR:
            setattr(self, log_type.lower(), self.cache_manager.get_cache(log_type).write)

    def _init_logger(self):
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(self.level)

    @property
    def console(self):
        return self._console

    @console.setter
    def console(self, value):
        self._console = bool(value)

        if self.console:
            self.enable_console_handle()

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, filename):
        self._filename = filename

        if self.filename:
            self.enable_log_file_handle(filename)

    def enable_console_handle(self, formatter=None):
        if not self.get_console_handle():
            console_handle = logging.StreamHandler(stream=sys.stdout)
            if formatter is None:
                formatter = self.FORMATTER
            console_handle.setFormatter(formatter)
            self.logger.addHandler(console_handle)

    def enable_log_file_handle(self, filename, mode='a', formatter=None):
        if not self.get_file_handle(filename):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError:
                pass

            file_handle = logging.FileHandler(filename, mode=mode)
            if formatter is None:
                formatter = self.FORMATTER
            file_handle.setFormatter(formatter)
            self.logger.addHandler(file_handle)

    def get_console_handle(self):
        for handle in self.logger.handlers:
            if isinstance(handle, logging.StreamHandler):
                return handle

    def get_file_handle(self, filename):
        for handle in self.logger.handlers:
            if isinstance(handle, logging.FileHandler) and handle.baseFilename == os.path.abspath(filename):
                return handle

    def get_child(self, suffix, level=logging.DEBUG, console=False, filename=None):
        if self.logger.root is not self.logger:
            suffix = '.'.join((self.name, suffix))

            return Logger(suffix, level=level, console=console, filename=filename)

    def __getattr__(self, item):
        try:
            return getattr(self.logger, item)
        except AttributeError:
            raise LoggerAttributeError("No Attribute name of {}".format(str(item)))

    @log_strip
    def info(self, msg):
        self.logger.info(msg)

    @log_strip
    def debug(self, msg):
        self.logger.debug(msg)

    @log_strip
    def critical(self, msg):
        self.logger.critical(msg)

    @log_strip
    def error(self, msg):
        self.logger.error(msg)

    @log_strip
    def warn(self, msg):
        self.logger.warn(msg)

    warning = warn

    def flush(self):
        # self.cache_manager.flush()
        for handle in self.logger.handlers:
            handle.flush()

    def __getstate__(self):
        log_dict = dict()
        log_dict['name'] = self.name
        log_dict['level'] = self.level
        log_dict['console'] = self.console
        log_dict['filename'] = self.filename
        self.__dict__['log_dict'] = log_dict
        odict = self.__dict__.copy()
        del odict['logger']
        return odict

    def __setstate__(self, state):
        log_dict = state['log_dict']
        del state['log_dict']
        self.__dict__.update(state)
        self._init_logger()
        self.console = log_dict['console']
        self.filename = log_dict['filename']


if __name__ == '__main__':
    logger1 = Logger('aaaa', level='DEBUG', filename='test1.log')
    logger2 = logger1.get_child('bbb', filename='test2.log')
    # logger2.addHandler(console_handle)

    logger1.debug('aa')
    logger2.info('bb')
    try:
        raise Exception('exception')
    except Exception as e:
        logger1.error(e.message)
    finally:
        logger1.error('aaa')
    # logger1.flush()
    # logger2.flush()
