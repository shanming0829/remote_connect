import socket
from contextlib import contextmanager

from core.decorators.decorators import must_connected, ftp_file_transform, thread_lock
from core.sessions.basic_session import BasicSession


class BasicFTPSession(BasicSession):
    def __init__(self, hostname, port, username=None, password=None, **kwargs):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password

        self._session = None
        self._connected = False

        self._connection_prototype = None

        super(BasicFTPSession, self).__init__(**kwargs)

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
                self.logger.debug('Connect to server successful ....')
                self._connected = connected
                self._session = session

    @must_connected
    def close(self):
        self._session.close()

    # @must_connected
    # def command(self, command, *args, **kwargs):
    #     return self._session.command(command, *args, **kwargs)

    @must_connected
    @ftp_file_transform
    def download_file(self, remote_file_path, local_file_path=None):
        pass

    @must_connected
    @ftp_file_transform
    def upload_file(self, local_file_path, remote_file_path=None):
        pass

    @must_connected
    def chdir(self, path):
        pass

    @must_connected
    def getcwd(self):
        pass

    @must_connected
    def listdir(self, path=''):
        pass

    @must_connected
    def mkdir(self, path, mode=511):
        pass

    @must_connected
    def normalize(self, path):
        pass

    @must_connected
    def remove(self, path):
        pass

    @must_connected
    def rmdir(self, path):
        pass

    @must_connected
    def rename(self, oldpath, newpath):
        pass

    @must_connected
    def stat(self, path):
        pass

    @contextmanager
    @must_connected
    def context_chdir(self, path):
        old_path = self.getcwd()
        self.chdir(path)
        yield
        self.chdir(old_path)

    def __getattr__(self, item):
        if hasattr(self._session, item):
            return getattr(self._session, item)

        raise AttributeError
