import unittest
from core.app import App
import pprint


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

        res = session.command('cd download; pwd')
        print(res)
        res = session.command('ls -lrt')
        print(res)

    def test_nx_session(self):
        session = self.app.nx_session

        login_command = 'ssh xchewan@seliius00519.seli.gic.ericsson.se'

        # res = session.command(login_command, prompt='Password:', timeout=30)
        # pprint.pprint(res)
        res = session.command(login_command, prompt=({'Password:': 'nT3bQfG7'},), timeout=30)
        pprint.pprint(res)
        res = session.command('ls -lrt')
        pprint.pprint(res)
