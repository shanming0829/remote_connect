import telnetlib

from core.context.contexts import switch_sock_read_timeout
from core.decorators.decorators import thread_lock
from core.sessions.shell import ShellSession, must_connected, CRLF


class TelnetSession(ShellSession):
    def __init__(self, hostname=None, port=23, username=None, password=None, **kwargs):
        super(TelnetSession, self).__init__(hostname, port, username, password, **kwargs)

    @must_connected
    def command_once(self, command, prompt=None, timeout=None):
        return self.command(command, prompt, timeout)

    def login(self, retry=3):
        self._connection_prototype = TelnetConnection
        return super(TelnetSession, self).login(retry)


class TelnetConnection(telnetlib.Telnet):
    def __init__(self, host=None, port=0, username=None, password=None, timeout=30, lock=None):
        self.connected = False

        self.username = username
        self.password = password
        self.lock = lock
        telnetlib.Telnet.__init__(self, host, port, timeout)

        self.login()

    @thread_lock
    def login(self):
        try:
            self.read_until("login:", self.timeout)
            self.write(self.username + "\n")
            if self.password:
                self.read_until("Password:", self.timeout)
                self.write(self.password + "\n")
            connected = True
        except:
            raise EnvironmentError
        else:
            self.connected = connected

    @thread_lock
    def write(self, buffer, enter=CRLF):
        telnetlib.Telnet.write(self, buffer + enter)

    @thread_lock
    def read(self, buffer_size, timeout=None):
        if timeout is not None and timeout != self.sock.gettimeout():
            with switch_sock_read_timeout(self.sock, timeout):
                return self.sock.recv(buffer_size)
        return self.sock.recv(buffer_size)

    def set_timeout(self, timeout):
        self.sock.settimeout(timeout)


if __name__ == '__main__':
    client = TelnetSession(hostname='192.168.33.10', username='test', password='test')
    # client.empty()
    res = client.command('cd dir1/dir2', prompt=r'[\r\n].*?\$')
    print(res)
    res = client.command('ls -lrt', prompt=r'[\r\n].*?\$')
    print(res)
