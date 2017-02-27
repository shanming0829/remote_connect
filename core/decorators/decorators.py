# -*- coding: UTF-8 -*-
import socket

from decorator import decorator
from core.context.contexts import thread_acquire_and_release
from core.utils.utility import list2str, dict2str

__authors__ = "Shanming Liu"


@decorator
def must_connected(func, self, *args, **kwargs):
    if not self.connected:
        self.logger.debug('Currently not login into server ....')
        self.login()

    return func(self, *args, **kwargs)


@decorator
def command_execute(func, self, command, *args, **kwargs):
    # for remain data parse
    try:
        self._session.read(self.buffer_size)
    except socket.timeout:
        pass

    self.logger.debug('Execute command -> {}'.format(command))
    # self.logger.debug('{} {}'.format(self.latest_prompt, command))

    res = func(self, command, *args, **kwargs)

    self.logger.debug('Response -> {}'.format(res))

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
