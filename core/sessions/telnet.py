# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import telnetlib

from core.sessions.exceptions.shell import ConnectionLoginException
from core.sessions.shell import ShellSession, must_connected, ShellConnection


class TelnetSession(ShellSession):
    def __init__(self, sid=None, hostname=None, port=23, username=None, password=None, logger=None, timeout=None,
                 crlf=None,
                 **kwargs):
        super(TelnetSession, self).__init__(
            sid=sid,
            hostname=hostname,
            port=port,
            username=username,
            password=password,
            logger=logger,
            timeout=timeout,
            crlf=crlf, **kwargs)

    @must_connected
    def command_once(self, command, prompt=None, timeout=None):
        return self.command(command, prompt, timeout)

    def login(self, retry=3):
        self._connection_prototype = TelnetConnection
        return super(TelnetSession, self).login(retry)


class TelnetConnection(telnetlib.Telnet, ShellConnection):
    def __init__(self, host=None, port=0, username=None, password=None, timeout=5, crlf=None):
        self.connected = False

        self.username = username
        self.password = password
        telnetlib.Telnet.__init__(self, host, port, timeout)
        ShellConnection.__init__(self, timeout=timeout, crlf=crlf)

        self.login()

        self.pipe_reader = self.sock.makefile('rb')

    def login(self):
        try:
            self.read_until("login:", self.timeout)
            self.write(self.username)
            if self.password:
                self.read_until("Password:", self.timeout)
                self.write(self.password)
            connected = True
        except Exception as e:
            raise ConnectionLoginException(e)
        else:
            self.connected = connected
            self.conn = self.sock

    def write(self, buffer):
        telnetlib.Telnet.write(self, buffer + self.crlf)


if __name__ == '__main__':
    client = TelnetSession(hostname='192.168.33.10', username='test', password='test')
    # client.empty()
    res = client.command('cd dir1/dir2', prompt=r'[\r\n].*?\$')
    print(res)
    res = client.command('ls -lrt', prompt=r'[\r\n].*?\$')
    print(res)
