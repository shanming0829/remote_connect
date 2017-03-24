# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from decorator import decorator
from core.context.contexts import thread_acquire_and_release
from core.log.log import Logger

__authors__ = "Shanming Liu"

logger = Logger()


@decorator
def must_connected(func, self, *args, **kwargs):
    if not self.connected:
        self.logger.debug('Currently not login into {} ....'.format(self.hostname))
        self.login()

    return func(self, *args, **kwargs)


@decorator
def command_execute(func, self, command, *args, **kwargs):
    self.empty()

    self.logger.flush()

    self.logger.info('Execute command -> {}'.format(command.command))

    res = func(self, command, *args, **kwargs)

    self.logger.debug('Matched prompt -> {}'.format(res.prompt.strip()))

    return res


@decorator
def ftp_file_transform(func, self, src, des, *args, **kwargs):
    self.logger.debug('{} file from {} to {}'.format(func.__name__, src, des))
    func(self, src, des, *args, **kwargs)
    self.logger.debug('{} file from {} to {} finished'.format(func.__name__, src, des))


@decorator
def ftp_command_execute(func, self, *args, **kwargs):
    self.logger.debug('Execute command -> {}({}, {})'.format(func.__name__, ','.join(args), ','.join(
        '{}={}'.format(k, v) for k, v in kwargs.iteritems()
    )))
    res = func(self, *args, **kwargs)
    self.logger.debug('Response -> {}'.format(res))
    return res


@decorator
def thread_lock(func, self, *args, **kwargs):
    with thread_acquire_and_release(self.lock):
        return func(self, *args, **kwargs)


def class_singleton(cls):
    _instances = {}

    def _singleton(*args, **kwargs):
        # instance_name = list2str(args) + "_" + dict2str(kwargs)
        instance_name = cls
        if instance_name not in _instances:
            _instances[instance_name] = cls(*args, **kwargs)
        return _instances[instance_name]

    return _singleton


class SingletonMeta(type):
    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instance


def test_step(msg):
    @decorator
    def wrapper_func(func, *args, **kwargs):
        logger.info(real_msg)
        return func(*args, **kwargs)

    def inner(*args, **kwargs):
        logger.info(real_msg)
        return msg(*args, **kwargs)

    if isinstance(msg, basestring):
        real_msg = 'Current step -> {}'.format(msg)
        return wrapper_func
    elif callable(msg):
        real_msg = 'Current step -> {}'.format(msg.__name__)
        return inner
    raise NotImplementedError("Not support other data type")
