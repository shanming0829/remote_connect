# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

import unittest
from pprint import pprint

from core import App
from core.sessions import SSHSession


class AppTest(unittest.TestCase):
    def setUp(self):
        self.app = App()
        self.app.load_config_file('../sessions.yaml')

    def test_copy_session(self):
        session1 = self.app.ssh_session

        session2 = self.app.copy_one_session(session1.sid, 'ssh_session2')

        self.assertIsInstance(session2, SSHSession)

        res = session2.command('ls -lrt')
        pprint(res)
