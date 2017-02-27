# -*- coding: UTF-8 -*-

import re
import socket
import time

from core.decorators.decorators import must_connected, command_execute
from core.sessions.basic_session import BasicSession

CRLF = "\r\n"


class ExecuteException(Exception):
    pass


class ExecuteTimeoutException(ExecuteException):
    pass


class ShellSession(BasicSession):
    def __init__(self, hostname, port, username, password, **kwargs):
        self.default_prompt = [re.compile(r'[\r\n].*?>'), re.compile(r'[\r\n].*?\$'), re.compile(r'[\r\n].*?%')]
        self.prompt = self.default_prompt
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.timeout = 5
        self.buffer_size = 1024
        self.read_timeout = 1
        self.read_duration = 0.01
        self.debug = False

        self._session = None
        self._connected = False
        self._connection_prototype = None

        self._latest_prompt = None

        super(ShellSession, self).__init__(**kwargs)

    @property
    def connected(self):
        return self._connected

    def login(self, retry=3):
        connected = False
        while not connected:
            try:
                self.logger.debug('Try connect to server {}'.format(str(self._connection_prototype)))
                self.logger.debug('hostname: {}, port: {}, username: {}, password: {}'.
                                  format(self.hostname, self.port, self.username, self.password))
                session = self._connection_prototype(self.hostname, self.port, self.username, self.password,
                                                     lock=self.lock)
                connected = True
            except socket.error as e:
                self.logger.debug('Connect to server failed, try reconnect ....')
                retry -= 1
                if retry <= 0:
                    raise e
                continue
            else:
                self.logger.debug('Connectted to server successful ....')
                self._connected = connected
                self._session = session
                self.empty()
            finally:
                if not connected and self._session:
                    self._session.close()

    def close(self):
        self._session.close()

    @must_connected
    @command_execute
    def command(self, command, prompt=None, timeout=None):
        self.set_prompt(prompt)
        self.set_timeout(timeout)
        res, p = self._execute(command)
        return res

    def _execute(self, command):
        start_time = time.time()
        res = ''
        self._session.write(command)

        while True:
            try:
                data = self._session.read(self.buffer_size)
                # self.logger.debug("Receive data -> {}".format(data))
            except socket.timeout:
                data = ''
            res += data

            match = self.find_regex_response(res)
            if match is not None:
                return self.parse_output(res, command, match)

            tmp_time = time.time()
            if tmp_time - start_time > self.timeout:
                raise ExecuteTimeoutException
            time.sleep(self.read_duration)

    @must_connected
    def empty(self):
        while True:
            try:
                login_data = self._session.read(self.buffer_size, timeout=1)
            except socket.timeout:
                login_data = ''

            if self.debug:
                print(login_data)
            time.sleep(1)
            if not login_data:
                break

    def set_prompt(self, prompt=None):
        if prompt is None:
            self.prompt = self.default_prompt
        elif isinstance(prompt, basestring):
            self.prompt = [re.compile(prompt)]
        elif isinstance(prompt, (tuple, list)):
            _prompt = []
            for i in prompt:
                _prompt.extend(self.set_prompt(i))
            self.prompt = _prompt
        elif isinstance(prompt, re._pattern_type):
            self.prompt = prompt
        else:
            raise TypeError

    def set_session_timeout(self, timeout=None):
        _timeout = timeout if timeout else self.read_timeout
        self._session.set_timeout(_timeout)

    def set_timeout(self, timeout=None):
        if timeout is not None:
            self.timeout = timeout

    def parse_output(self, res, command, prompt):
        # self.logger.debug("Expected prompt ->{}, match result->{}".format(prompt, res))
        self.latest_prompt = prompt
        return res[res.index(command) + len(command) + 1: res.rindex(prompt)].strip(), prompt

    def find_regex_response(self, res):
        for _p in self.prompt:
            match = _p.search(res)
            if match:
                return match.group()

    @property
    def latest_prompt(self):
        return self._latest_prompt

    @latest_prompt.setter
    def latest_prompt(self, prompt):
        self._latest_prompt = prompt
