# -*- coding: UTF-8 -*-
__authors__ = "Shanming Liu"

class AttributeDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttributeDict, self).__init__(*args, **kwargs)

    def __setattr__(self, name, value):
        self[name] = value

    def __getattr__(self, item):
        if item in self:
            return self[item]
        raise AttributeError


if __name__ == '__main__':
    d = AttributeDict()
    print(d.__dict__)
    print(d.a)
    print(d.b)
    print(d.c)
