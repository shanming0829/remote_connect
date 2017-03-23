# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

import abc
# from threading import RLock


class ClosingContextManager(object):
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()


class BasicSession(ClosingContextManager):
    __metaclass__ = abc.ABCMeta

    def __init__(self, sid, hostname, port, username, password, logger, **kwargs):
        self.sid = sid
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.logger = logger
        self.__dict__.update(kwargs)

        # self.lock = RLock()
        super(BasicSession, self).__init__()

    @abc.abstractmethod
    def login(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def close(self):
        raise NotImplementedError
