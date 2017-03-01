# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import os
import paramiko

from core.decorators.decorators import ftp_command_execute, thread_lock
from core.sessions.basic_ftp import BasicFTPSession


class SFTPSession(BasicFTPSession):
    def __init__(self, sid=None, hostname=None, port=22, username=None, password=None, **kwargs):
        super(SFTPSession, self).__init__(
            sid=sid,
            hostname=hostname,
            port=port,
            username=username,
            password=password, **kwargs)

    def login(self, retry=3):
        self._connection_prototype = SFTPConnection
        return super(SFTPSession, self).login(retry)

    @thread_lock
    def upload_file(self, local_file_path, remote_file_path=None):
        super(SFTPSession, self).upload_file(local_file_path, remote_file_path)
        local_file_name = os.path.basename(local_file_path)
        remote_file_path = remote_file_path if remote_file_path else local_file_name
        self._session.put(local_file_path, remote_file_path)

    @thread_lock
    def download_file(self, remote_file_path, local_file_path=None):
        super(SFTPSession, self).download_file(remote_file_path, local_file_path)
        remote_file_name = os.path.basename(remote_file_path)
        local_file_path = local_file_path if local_file_path else remote_file_name
        self._session.get(remote_file_name, local_file_path)

    @ftp_command_execute
    def listdir(self, path=''):
        super(SFTPSession, self).listdir(path)
        return self._session.listdir(path)

    @ftp_command_execute
    def mkdir(self, path, mode=511):
        super(SFTPSession, self).mkdir(path, mode)
        return self._session.mkdir(path, mode)

    @ftp_command_execute
    def getcwd(self):
        super(SFTPSession, self).getcwd()
        return self._session.getcwd()

    @ftp_command_execute
    def rmdir(self, path):
        super(SFTPSession, self).rmdir(path)
        return self._session.rmdir(path)

    @ftp_command_execute
    def rename(self, oldpath, newpath):
        super(SFTPSession, self).rename(oldpath, newpath)
        return self._session.rename(oldpath, newpath)

    @ftp_command_execute
    def chdir(self, path):
        super(SFTPSession, self).chdir(path)
        return self._session.chdir(path)

    @ftp_command_execute
    def remove(self, path):
        super(SFTPSession, self).remove(path)
        return self._session.remove(path)

    @ftp_command_execute
    def normalize(self, path):
        super(SFTPSession, self).normalize(path)
        return self._session.normalize(path)

    @ftp_command_execute
    def stat(self, path):
        super(SFTPSession, self).stat(path)
        return self._session.stat(path)


class SFTPConnection(paramiko.SFTPClient):
    def __init__(self, hostname, port=22, username='', password='', timeout=30, lock=None):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.lock = lock

        self.chan = self.generate_channel()
        super(SFTPConnection, self).__init__(self.chan)

    def generate_channel(self, window_size=None, max_packet_size=None):
        transport = paramiko.Transport((self.hostname, self.port))
        transport.connect(username=self.username, password=self.password)

        chan = transport.open_session(window_size=window_size, max_packet_size=max_packet_size)
        if chan is None:
            return None
        chan.invoke_subsystem('sftp')
        return chan


if __name__ == '__main__':
    client = SFTPSession('192.168.33.10', username='test', password='test')
    res = client.stat('download')
    print(res.__dict__)
