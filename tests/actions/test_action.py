# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

import unittest
from core.app import App
from pprint import pprint


class AppTest(unittest.TestCase):
    def setUp(self):
        self.app = App()
        self.app.load_config_file('sessions.yaml')

    def test_action(self):
        session = self.app.ssh_session

        res = session.command('python mulit_input.py',
                              prompt=[('Please input node password:', 'aaaa'), ('Please confirm \[y/n\]', 'y')])
        pprint(res)
