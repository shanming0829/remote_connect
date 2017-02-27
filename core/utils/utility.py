# -*- coding: UTF-8 -*-

__authors__ = "Shanming Liu"


def list2str(_list, link='_'):
    return link.join(str(i) for i in _list)


def dict2str(_dict, link="_"):
    return link.join("{}_{}".format(k, str(v)) for k, v in _dict.items())
