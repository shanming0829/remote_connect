# -*- coding: UTF-8 -*-


class ShellSessionException(Exception):
    pass


class ExecuteException(Exception):
    pass


class ExecuteTimeoutException(ExecuteException):
    pass


class ShellConnectionReadException(Exception):
    pass


class ConnectionLoginException(Exception):
    pass
