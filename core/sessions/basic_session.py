# -*- coding: UTF-8 -*-

import abc
from threading import RLock

from core.log.log import Logger


class ClosingContextManager(object):
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()


class BasicSession(ClosingContextManager):
    __metaclass__ = abc.ABCMeta

    def __init__(self, logger=None, **kwargs):
        self.logger = logger if logger else Logger(self.__class__.__name__, level='DEBUG')
        self.__dict__.update(kwargs)

        self.lock = RLock()
        super(BasicSession, self).__init__()

    @abc.abstractmethod
    def login(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def close(self):
        raise NotImplementedError
