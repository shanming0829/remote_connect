# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import paramiko

from core.sessions.exceptions.shell import ConnectionLoginException
from core.sessions.shell import ShellSession, must_connected, ShellConnection


class SSHSession(ShellSession):
    def __init__(self, sid=None, hostname=None, port=22, username=None, password=None, logger=None, timeout=None,
                 crlf=None,
                 **kwargs):
        super(SSHSession, self).__init__(
            sid=sid,
            hostname=hostname,
            port=port,
            username=username,
            password=password,
            logger=logger,
            timeout=timeout,
            crlf=crlf,
            **kwargs)

    @must_connected
    def command_once(self, command, prompt=None, timeout=None):
        stdin, stdout, stderr = self._session.exec_command(command, timeout=timeout)
        return stdout.read()

    def login(self, retry=3):
        self._connection_prototype = SSHConnection
        return super(SSHSession, self).login(retry)

    def open_sftp(self):
        return self._session.open_sftp()


class SSHConnection(paramiko.SSHClient, ShellConnection):
    def __init__(self, hostname=None, port=0, username=None, password=None, timeout=5, crlf=None):
        self.connected = None
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout

        self.conn = None

        paramiko.SSHClient.__init__(self)
        ShellConnection.__init__(self, timeout=timeout, crlf=crlf)

        self.login()

    def login(self):
        try:
            self.load_system_host_keys()
            self.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            self.connect(self.hostname, port=self.port, username=self.username, password=self.password,
                         timeout=self.timeout)
            connected = True
        except (paramiko.AuthenticationException, paramiko.PasswordRequiredException, paramiko.SSHException) as e:
            raise ConnectionLoginException(e)
        else:
            self.connected = connected
            self.conn = self.invoke_shell()
            self.rlist = [self.conn, ]

    def write(self, buffer):
        self.conn.sendall(buffer + self.crlf)


if __name__ == '__main__':
    client = SSHSession(hostname='192.168.33.10', username='test', password='test')
    res = client.command('cd dir1/dir2')
    print(res)
    res = client.command('ls -lrt')
    print(res)
