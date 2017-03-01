# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

from core import AttributeDict
from ConfigParser import ConfigParser
import pprint

__authors__ = "Shanming Liu"

config = ConfigParser(dict_type=AttributeDict)

config.read('config.ini')

for section in config.sections():
    pprint.pprint(config.items(section))
