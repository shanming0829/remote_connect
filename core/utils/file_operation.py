# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

__authors__ = "Shanming Liu"


def get_des_file_name(src, des):
    if des is None:
        if hasattr(src, 'name'):
            return getattr(src, 'name')
        elif isinstance(src, basestring):
            return src
        else:
            raise TypeError
    elif isinstance(des, basestring):
        return des
    elif isinstance(des, file):
        return des.name
    else:
        raise TypeError


def convert_to_file_object(name, mode='r'):
    if isinstance(name, basestring):
        return open(name, mode=mode)
    elif hasattr(name, 'write') and hasattr(name, 'read'):
        return name
    else:
        raise TypeError


def convert_file_object_to_str(fileobj, check_type=file):
    if isinstance(fileobj, check_type):
        fileobj.close()
        return fileobj.name
    elif isinstance(fileobj, basestring):
        return fileobj
    raise TypeError
