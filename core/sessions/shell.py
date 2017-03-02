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
from core.sessions.session_util import CommandPrompt, Command


class ShellSession(BasicSession):
    def __init__(self, sid=None, hostname=None, port=None, username=None, password=None, logger=None, timeout=None,
                 crlf=None,
                 **kwargs):
        self.default_prompt = [CommandPrompt(prompt=i, action=None) for i in
                               (r'[\r\n].*?>', r'[\r\n].*?\$', r'[\r\n].*?%')]
        self.prompt = self.default_prompt
        self.default_timeout = timeout
        self.match_prompt = None
        self.timeout = self.default_timeout
        self.crlf = crlf
        self.buffer_size = 8192
        self.read_timeout = 1
        self.read_duration = 0.1

        self._session = None
        self._connected = False
        self._connection_prototype = None

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

        # res = list()

        command = Command(command=command, prompt=self.prompt, timeout=self.timeout)
        while command:
            response = self._execute(command, self.read_data_writer)

            # res.append(response)

            if response.action:
                command = Command(command=response.action, prompt=self.default_prompt, timeout=self.timeout)
            else:
                command = None

        return response

    @thread_lock
    def _execute(self, command, callback=None):
        start_time = time.time()
        res = ''
        self._session.write(command.command)

        while True:
            try:
                data = self._session.read(self.buffer_size)
                if callback:
                    callback(data)
            except ShellConnectionReadException:
                tmp_time = time.time()
                if tmp_time - start_time > command.timeout:
                    raise ExecuteTimeoutException(
                        "Not match the expected prompt ->{}, timeout ->{}".format(
                            ','.join(str(i) for i in command.prompt),
                            command.timeout))
                time.sleep(self.read_duration)
                continue
            else:
                res += data
                response = command.parse_output(res)
                if response.status:
                    return response

    def empty(self, retry=3):
        while True:
            try:
                remain_data = self._session.read(self.buffer_size, timeout=0.1)
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
        elif isinstance(prompt, (basestring, re._pattern_type)):
            self.prompt = [CommandPrompt(prompt=prompt, action=None)]
        elif isinstance(prompt, (tuple, list)):
            _prompt = list()
            for i in prompt:
                if isinstance(i, basestring):
                    _prompt.append(CommandPrompt(prompt=i, action=None))
                elif isinstance(i, (tuple, list)):
                    _prompt.append(CommandPrompt(*i[:2]))
                elif isinstance(i, dict):
                    _prompt.extend([CommandPrompt(k, v) for k, v in i.iteritems()])
                else:
                    raise TypeError
            self.prompt = _prompt
        elif isinstance(prompt, dict):
            self.prompt = [CommandPrompt(k, v) for k, v in prompt.iteritems()]
        else:
            raise TypeError

    def set_timeout(self, timeout=None):
        if timeout is not None:
            self.timeout = timeout
        else:
            self.timeout = self.default_timeout


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
