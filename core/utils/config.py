# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

import yaml

from core.decorators.decorators import class_singleton, SingletonMeta
from core.utils.attribuate_dict import AttributeDict

__authors__ = "Shanming Liu"


class _Config(AttributeDict):
    __metaclass__ = SingletonMeta

    def load_config_file(self, config_file):
        if config_file.endswith('.yaml'):
            self._load_yaml_config(config_file)

        elif self.config_file.endswith('.ini'):
            self._load_ini_config(config_file)

    def _load_yaml_config(self, config_file):
        with open(config_file) as f:
            self.update_dict(**yaml.load(f))

    def _load_ini_config(self, config_file):
        pass


Config = _Config

if __name__ == '__main__':
    config1 = Config()
    config1.load_config_file('G:\\Project\\remote_connect\\tests\\sessions.yaml')
    import pprint

    pprint.pprint(config1)
