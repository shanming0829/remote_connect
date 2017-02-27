# -*- coding: UTF-8 -*-

import functools

__authors__ = "Shanming Liu"


def log_context(logger, begin='*' * 100, end='*' * 100, level='DEBUG'):
    """
    Divide different log do somethings.
    """

    def wrapper(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            log = getattr(logger, level.lower())
            log(begin)
            res = func(*args, **kwargs)
            log(end)
            return res

        return inner

    return wrapper
