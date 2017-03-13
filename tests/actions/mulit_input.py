# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

__authors__ = "Shanming Liu"

password = 'aaaa'

while True:
    res = raw_input('Please input node password:')
    if res == password:
        break

while True:
    res = raw_input('Please confirm [y/n]')
    if res in ['Y', 'y']:
        print('You confirm this operation.')
        print('a' * 100)
        print('b' * 100)
        print('c' * 100)
        break
    elif res in ['n', 'N']:
        print('You not accept this operation. System exit')
        break
    else:
        print('Your input error.')
