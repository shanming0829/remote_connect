import yaml
import weakref
from core import App
from core.session_manager import SessionManager

import unittest


class SessionManagerTest(unittest.TestCase):
    def setUp(self):
        self.app = App('sessions.yaml')

    def test_telnet_session(self):
        telnet_session = self.app.session_manager.get_session('telnet_session')

        res = telnet_session.command('pwd')
        print res

    def test_weakref_session(self):
        ssh_session = self.app.ssh_session
        ssh_session.command('ls')

        self.assertEqual(1, weakref.getweakrefcount(self.app.session_manager.sessions['ssh_session']))
