import unittest

from core import Logger
from core.app import App
import pprint
import signal
import cPickle
import sys

import logging


def process_test(app):
    pass


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

    def test_pick(self):
        self.app.ssh_session.command('ls')
        with open('test_pickle.txt', 'w') as f:
            cPickle.dump(self.app, f)

        app = cPickle.load(open('test_pickle.txt'))
        app.ssh_session.command('ls')


class LoggerTest(unittest.TestCase):
    def test_pick_logger(self):
        logger = Logger('runner', console=True, filename='a.log')
        cPickle.dump(logger, sys.stdout)

    def test_origin_logger(self):
        logger = logging.getLogger('runner')
        logger.addHandler(logging.FileHandler('runner.log'))
        cPickle.dump(logger, sys.stdout)
