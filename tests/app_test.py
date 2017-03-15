import unittest
from core.app import App
import pprint
import signal

class AppTest(unittest.TestCase):
    def setUp(self):
        self.app = App()
        self.app.load_config_file('sessions.yaml')

    def test_telnet_session(self):
        session = self.app.telnet_session

        res = session.command('cd download; pwd')
        print(res)
        res = session.command('ls -lrt')
        print(res)

    def test_ssh_session(self):
        session = self.app.ssh_session

        # res = session.command('cd download; pwd')
        # print(res)
        res = session.command('^C')
        print(res)

        # res = session.command('ls -lrt')
        # print(res)
