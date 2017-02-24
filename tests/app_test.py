import unittest
from core.app import App
from core.sessions import TelnetSession

# class AppTest(unittest.TestCase):
#     def setUp(self):
#         self.app = App()
#         self.app.load_config_file('sessions.yaml')
#
#     def test_telnet_session(self):
#         telnet_session = self.app.telnet_session
#
#         self.assertIsInstance(telnet_session, TelnetSession)


app = App('sessions.yaml')
res = app.telnet_session.command('cd download; pwd')
print(res)

res = app.telnet_session.command('ls -lrt')
print(res)
