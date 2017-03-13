# -*- Coding: UTF-8 -*-
from __future__ import unicode_literals

import os
import datetime

from core.decorators.decorators import class_singleton
from core.session_manager import SessionManager
from core.log.log import Logger
from core.utils.attribuate_dict import AttributeDict
from core.utils.config import Config

__authors__ = "Shanming Liu"


class AppException(RuntimeError):
    pass


@class_singleton
class App(object):
    def __init__(self, config_path=None):
        self.session_manager = None

        self.config = None

        self.logger = None

        if config_path:
            self.load_config_file(config_path)

    def load_config_file(self, config_path):
        self.config = Config()
        self.config.load_config_file(config_path)

        self._fix_config()

        self._fix_sessions()

        self._init_log()

        self._init_sessions()

    def _fix_config_log(self, console=True, log_level=None, log_dir=None, log_file=None):
        self.config.config.log.console = bool(console)
        self.config.config.log.level = 'INFO' if log_level is None else log_level
        tmp_dir = os.path.abspath('logs' if log_dir is None else log_dir)
        self.config.config.log.dir = os.path.join(tmp_dir, datetime.datetime.today().strftime('%Y%m%d_%H%M%S'))
        self.config.config.log.file = 'runner.log' if log_file is None else log_file

    def _fix_config_session(self, crlf=None, timeout=None):
        self.config.config.session.crlf = '\r\n' if crlf is None else crlf
        self.config.config.session.timeout = 5 if timeout is None else timeout

    def _fix_config(self):
        if 'config' not in self.config:
            self.config.config = AttributeDict()
            self.config.config.log = AttributeDict()
            self.config.config.session = AttributeDict()
        elif 'config' in self.config:
            if 'log' not in self.config.config:
                self.config.config.log = AttributeDict()
            if 'session' not in self.config.config:
                self.config.config.session = AttributeDict()

        self._fix_config_log(
            console=self.config.config.log.get('console', True),
            log_level=self.config.config.log.get('level', None),
            log_dir=self.config.config.log.get('dir', None),
            log_file=self.config.config.log.get('file', None)
        )

        self._fix_config_session(
            crlf=self.config.config.session.get('crlf', None),
            timeout=self.config.config.session.get('timeout', None)
        )

    def _fix_session_config(self, session_name, session_config):
        tmp_config = AttributeDict()
        # add log level for each session
        tmp_config.level = self.config.config.log.level

        tmp_config.update_dict(**self.config.config.session)
        tmp_config.update_dict(**session_config)

        setattr(self.config.sessions, session_name, tmp_config)

    def _fix_sessions(self):
        if 'sessions' not in self.config:
            raise AppException("No sessions found in config file, system exit.")

        for session_name, session_config in self.config.sessions.iteritems():
            self._fix_session_config(session_name, session_config)

    def _init_log(self):
        self.logger = Logger('runner', level=self.config.config.log.level,
                             console=self.config.config.log.console)
        log_path = os.path.join(self.config.config.log.dir, self.config.config.log.file)
        self.logger.enable_log_file_handle(log_path)

    def _init_sessions(self):

        self.session_manager = SessionManager(self.logger)

        for name, session in self.session_manager.create_sessions().iteritems():
            setattr(self, name, session)

    def copy_one_session(self, src_name, dst_name):
        """
        Copy one session by the source session sid, the src_name should not equal with dst_name
        :param src_name: Source session sid.
        :param dst_name: Destination session sid.
        :return: Session instance
        """
        if src_name == dst_name:
            raise AppException('The src_name should not equal with dst_name')

        if src_name not in self.config.sessions:
            raise AppException('Can not find any source session instance,')
        dst_session = self.session_manager.copy_one_session(src_name, dst_name)
        setattr(self, dst_name, dst_session)

        return dst_session
