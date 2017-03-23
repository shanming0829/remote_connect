# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import yaml

import pprint

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

    def update_dict(self, **kwargs):
        for k, v in kwargs.iteritems():
            if isinstance(v, (basestring, int, float)):
                self[k] = v
            elif isinstance(v, (dict, AttributeDict)):
                tmp_dict = AttributeDict()
                if k in self:
                    tmp_dict.update_dict(**self[k])
                tmp_dict.update_dict(**v)
                self[k] = tmp_dict
            elif isinstance(v, (tuple, list)):
                tmp_list = []
                if k in self:
                    tmp_list.extend(self[k])
                tmp_list.extend(v)
                self[k] = self.update_list(*tmp_list)

    def update_list(self, *args):
        values = []
        for item in args:
            if isinstance(item, (basestring, int, float, AttributeDict)):
                values.append(item)
            elif isinstance(item, dict):
                tmp_dict = AttributeDict()
                tmp_dict.update_dict(**item)
                values.append(tmp_dict)
            elif isinstance(item, (tuple, list)):
                values.append(self.update_list(*item))

        return values

    def load_yaml_file(self, filename):
        with open(filename) as f:
            self.update_dict(**yaml.load(f))

    def load_ini_file(self, filename):
        pass


if __name__ == '__main__':
    d = AttributeDict()
    # d.update_dict(a=10, b={'c': 20, 'd': 30, 'e': [1, [2, 3]]})
    # print(d.b.e)

    d.a.b.c = 10

    pprint.pprint(d)
