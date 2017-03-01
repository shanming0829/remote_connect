# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
import re
import socket
import time
import select

from core.decorators.decorators import must_connected, command_execute, thread_lock
from core.sessions.basic_session import BasicSession
from core.sessions.exceptions.shell import ShellConnectionReadException, ExecuteTimeoutException


class ShellSession(BasicSession):
    def __init__(self, sid=None, hostname=None, port=None, username=None, password=None, logger=None, timeout=None,
                 crlf=None,
                 **kwargs):
        self.default_prompt = [re.compile(r'[\r\n].*?>'), re.compile(r'[\r\n].*?\$'), re.compile(r'[\r\n].*?%')]
        self.prompt = self.default_prompt
        self.default_timeout = timeout
        self.timeout = self.default_timeout
        self.crlf = crlf
        self.buffer_size = 8192
        self.read_timeout = 1
        self.read_duration = 0.1

        self._session = None
        self._connected = False
        self._connection_prototype = None

        self._latest_prompt = None

        super(ShellSession, self).__init__(sid, hostname, port, username, password, logger, **kwargs)

    @property
    def connected(self):
        return self._connected

    def login(self, retry=3):
        connected = False
        while not connected:
            try:
                self.logger.info('Try connect to {}.'.format(self.hostname))
                self.logger.debug('hostname: {}, port: {}, username: {}, password: {}'.
                                  format(self.hostname, self.port, self.username, self.password))
                session = self._connection_prototype(self.hostname, self.port, self.username, self.password,
                                                     timeout=self.read_timeout, crlf=self.crlf,
                                                     lock=self.lock)
                connected = True
            except socket.error as e:
                self.logger.info('Connect to server failed, try reconnect ....')
                retry -= 1
                if retry <= 0:
                    raise e
                continue
            else:
                self.logger.info('Connected to {} succeed.'.format(self.hostname))
                self._connected = connected
                self._session = session
            finally:
                if not connected and self._session:
                    self._session.close()

    def close(self):
        self._session.close()

    def read_data_writer(self, data):
        self.logger.debug(data)

    @must_connected
    @command_execute
    def command(self, command, prompt=None, timeout=None):
        self.set_prompt(prompt)
        self.set_timeout(timeout)
        res, p = self._execute(command, self.read_data_writer)
        return res

    @thread_lock
    def _execute(self, command, callback=None):
        start_time = time.time()
        res = ''
        self._session.write(command)

        while True:
            try:
                data = self._session.read(self.buffer_size)
                if callback:
                    callback(data)
            except ShellConnectionReadException:
                tmp_time = time.time()
                if tmp_time - start_time > self.timeout:
                    raise ExecuteTimeoutException(
                        "Not match the expected prompt ->{}, timeout ->{}".format(str([i.pattern for i in self.prompt]),
                                                                                  self.timeout))
                time.sleep(self.read_duration)
                continue
            else:
                res += data
                match = self.find_regex_response(res)
                if match is not None:
                    return self.parse_output(res, command, match)

    def empty(self, retry=3):
        while True:
            try:
                remain_data = self._session.read(self.buffer_size, timeout=1)
            except ShellConnectionReadException:
                retry -= 1
                if retry == 0:
                    break
                time.sleep(self.read_duration)
                continue
            else:
                self.logger.debug(remain_data)

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
            self.prompt = [prompt]
        else:
            raise TypeError

    def set_timeout(self, timeout=None):
        if timeout is not None:
            self.timeout = timeout
        else:
            self.timeout = self.default_timeout

    def parse_output(self, res, command, prompt):
        self.latest_prompt = prompt.strip()
        if command in res:
            return res[res.index(command) + len(command) + 1: res.rindex(prompt)].strip(), prompt
        return res[: res.rindex(prompt)].strip(), prompt

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


class ShellConnection(object):
    def __init__(self, timeout=None, crlf=None):
        self.timeout = timeout
        self.crlf = crlf

        self.conn = None

        self.rlist = [self, ]
        self.wlist = list()
        self.xlist = list()

    def write(self, buffer):
        raise NotImplementedError

    def read(self, buffer_size, timeout=None):
        if timeout:
            rlist, _, _ = select.select(self.rlist, self.wlist, self.xlist, timeout)
        else:
            rlist, _, _ = select.select(self.rlist, self.wlist, self.xlist, self.timeout)
        if len(rlist) > 0:
            return self.conn.recv(buffer_size)
        raise ShellConnectionReadException
