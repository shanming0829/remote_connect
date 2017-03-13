# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

import unittest
import os
from core.app import App
from pprint import pprint


class AppTest(unittest.TestCase):
    def setUp(self):
        self.app = App()
        self.app.load_config_file('sessions.yaml')

    def test_multi_input(self):
        session = self.app.ssh_session

        session.command('cd {}'.format(os.getcwd()))
        res = session.command('python mulit_input.py',
                              prompt=[('Please input node password:', 'aaaa'), ('Please confirm \[y/n\]', 'n')])
        pprint(res)

    def test_sleep_input(self):
        session = self.app.ssh_session
        session.command('cd {}'.format(os.getcwd()))
        res = session.command('python sleep_input.py',
                              prompt=[('Please input node password:', 'aaaa'), ('Please confirm \[y/n\]', 'n')],
                              timeout=10)
        pprint(res)
