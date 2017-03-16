# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
import re
import socket
import time
import select

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from core.decorators.decorators import must_connected, command_execute, thread_lock
from core.sessions.basic_session import BasicSession
from core.sessions.exceptions.shell import ShellConnectionReadException, ExecuteTimeoutException, ExecuteException
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

        self.command_output = None

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
                                                     timeout=self.read_timeout, crlf=self.crlf)
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

    @property
    def readable(self):
        return self._session.readable()

    def socket_data_receive(self, data):
        self.command_output.write(data)
        self.logger.debug(data)

    @must_connected
    def command(self, command, prompt=None, timeout=None):
        self.set_prompt(prompt)
        self.set_timeout(timeout)

        self.command_output = StringIO()
        response = None

        command = Command(command=command, prompt=self.prompt, timeout=self.timeout)
        while command:
            response = self._execute(command)

            if response.action is not None:
                sub_prompt = self.prompt + self.default_prompt
                command = Command(command=response.action, prompt=sub_prompt, timeout=self.timeout)
            else:
                command = None
        response.output = self.command_output.getvalue()
        return response

    # @thread_lock
    @command_execute
    def _execute(self, command):
        command_output = StringIO()
        response = None
        end_time = time.time() + command.timeout
        remain_data = ''
        matched = False
        self._session.write(command.command)

        def call_back(data):
            command_output.write(data)
            self.socket_data_receive(data)

        while self.readable:
            try:
                response = self._expected(command, end_time, call_back, init=remain_data, matched=matched)
            except ExecuteTimeoutException as e:
                raise e
            except ExecuteException:
                pass
            else:
                match_index = response.output.rindex(response.prompt) + len(response.prompt)
                remain_data = response.output[match_index + 1:]
                matched = True

        response.output = command_output.getvalue()
        response.response = response.output[:response.output.rindex(response.prompt)]
        if command.command in response.response:
            response.response = response.response[
                                response.response.index(command.command) + len(command.command) + 1:].strip()
        return response

    def _expected(self, command, end_time, callback, init='', matched=False):
        res = StringIO()
        res.write(init)

        condition = lambda: self.readable if matched else lambda: True

        while condition():
            try:
                data = self._session.read(self.buffer_size)
            except ShellConnectionReadException:
                if time.time() > end_time:
                    raise ExecuteTimeoutException(
                        "Not match the expected prompt ->{}, timeout ->{}".format(
                            ','.join(str(i) for i in command.prompt),
                            command.timeout))
            else:
                callback(data)
                res.write(data)
                response = command.parse_output(res.getvalue())

                if response.status:
                    return response
        else:
            raise ExecuteException('No data in socket.')

    def empty(self, retry=3):
        while self.readable and retry > 0:
            self.socket_data_receive(self._session.read(self.buffer_size, timeout=0.1))
            retry -= 1

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
                elif i is None:
                    _prompt.extend(self.default_prompt)
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

    def readable(self, timeout=None):
        if timeout:
            rlist, _, _ = select.select(self.rlist, self.wlist, self.xlist, timeout)
        else:
            rlist, _, _ = select.select(self.rlist, self.wlist, self.xlist, self.timeout)

        return True if len(rlist) > 0 else False

    def read(self, buffer_size, timeout=None):
        if self.readable(timeout):
            return self.conn.recv(buffer_size)
        raise ShellConnectionReadException
