# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from decorator import decorator
from core.context.contexts import thread_acquire_and_release

__authors__ = "Shanming Liu"


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


@decorator
def log_strip(func, self, msg, *args, **kwargs):
    msg = msg.strip()
    if msg:
        func(self, msg, *args, **kwargs)
