import socket

import paramiko

from core.context.contexts import switch_sock_read_timeout
from core.decorators.decorators import thread_lock
from core.sessions.shell import ShellSession, must_connected, CRLF


class SSHSession(ShellSession):
    def __init__(self, hostname=None, port=22, username=None, password=None, logger=None, **kwargs):
        super(SSHSession, self).__init__(hostname, port, username, password, logger=logger, **kwargs)

    @must_connected
    def command_once(self, command, prompt=None, timeout=None):
        stdin, stdout, stderr = self._session.exec_command(command, timeout=timeout)
        return stdout.read()

    def login(self, retry=3):
        self._connection_prototype = SSHConnection
        return super(SSHSession, self).login(retry)


class SSHConnection(paramiko.SSHClient):
    def __init__(self, hostname=None, port=0, username=None, password=None, timeout=30, lock=None):
        self.connected = None
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.lock = lock

        self.chan = None

        paramiko.SSHClient.__init__(self)

        self.login()

    @thread_lock
    def login(self):
        try:
            self.load_system_host_keys()
            self.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            self.connect(self.hostname, port=self.port, username=self.username, password=self.password)
            connected = True
        except (paramiko.AuthenticationException, paramiko.PasswordRequiredException, paramiko.SSHException) as e:
            raise e
        else:
            self.connected = connected
            self.chan = self.invoke_shell()
            self.chan.settimeout(self.timeout)

    @thread_lock
    def write(self, buffer, enter=CRLF):
        self.chan.sendall(buffer + enter)

    @thread_lock
    def read(self, buffer_size, timeout=None):
        if timeout is not None and timeout != self.chan.gettimeout():
            with switch_sock_read_timeout(self.chan, timeout):
                return self.chan.recv(buffer_size)
        return self.chan.recv(buffer_size)

    def set_timeout(self, timeout):
        self.chan.settimeout(timeout)


if __name__ == '__main__':
    client = SSHSession(hostname='192.168.33.10', username='test', password='test')
    res = client.command('cd dir1/dir2')
    print(res)
    res = client.command('ls -lrt')
    print(res)
