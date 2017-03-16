# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import os
from contextlib import contextmanager

__authors__ = "Shanming Liu"


@contextmanager
def cd(path):
    cur = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(cur)
