# -*- Coding: UTF-8 -*-

import os
import yaml

from core.session_manager import SessionManager
from core.log.log import Logger

__authors__ = "Shanming Liu"


class AppException(RuntimeError):
    pass


class App(object):
    def __init__(self, config_path=None):
        self.session_manager = None

        self.config = None

        self.logger = None

        if config_path:
            self.load_config_file(config_path)

    def load_config_file(self, config_path):
        self.config = yaml.load(open(config_path))

        self._init_log()

        self._init_sessions()

    def _init_log(self):
        if 'config' in self.config and 'log' in self.config['config']:
            log_config = self.config['config']['log']
            self.logger = Logger('runner', level=log_config.get('level', 'INFO'),
                                 console=log_config.get('console', True))

            log_dir = log_config['dir'] if 'dir' in log_config else 'logs'
            log_file = log_config['file'] if 'file' in log_config else 'runner.log'
            self.logger.enable_log_file_handle(os.path.join(log_dir, log_file))

        else:
            self.logger = Logger('runner')

    def _init_sessions(self):
        if 'sessions' not in self.config:
            raise AppException("No sessions found in config file, system exit.")

        self.session_manager = SessionManager(self.config['sessions'], self.logger)

        for name, session in self.session_manager.create_sessions().iteritems():
            setattr(self, name, session)
