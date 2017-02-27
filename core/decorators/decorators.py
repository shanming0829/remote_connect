# -*- coding: UTF-8 -*-
__authors__ = "Shanming Liu"

from decorator import decorator
from core.context.contexts import thread_acquire_and_release


@decorator
def must_connected(func, self, *args, **kwargs):
    if not self.connected:
        self.logger.debug('Currently not login into server ....')
        self.login()

    return func(self, *args, **kwargs)


@decorator
def command_execute(func, self, command, *args, **kwargs):
    # self.logger.debug('Execute command -> {}'.format(command))
    self.logger.debug('{} {}'.format(self.latest_prompt, command))

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
