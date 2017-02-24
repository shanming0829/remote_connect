import yaml
from core.session_manager import SessionManager

import unittest


class SessionManagerTest(unittest.TestCase):
    def setUp(self):
        super(SessionManagerTest, self).setUp()

        config = yaml.load(open('sessions.yaml'))

        self.manager = SessionManager(config.get('sessions'))

    def test_telnet_session(self):
        telnet_session = self.manager.get_session('telnet_session')

        res = telnet_session.command('pwd')
        print res
