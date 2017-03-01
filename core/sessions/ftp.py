# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import ftplib
import os

from core.decorators.decorators import ftp_command_execute, thread_lock
from core.utils.attribuate_dict import AttributeDict
from core.sessions.basic_ftp import BasicFTPSession
from core.sessions.exceptions.ftp import FTPSessionException


class FTPSession(BasicFTPSession):
    def __init__(self, sid=None, hostname=None, port=21, username=None, password=None, **kwargs):
        super(FTPSession, self).__init__(
            sid=sid,
            hostname=hostname,
            port=port,
            username=username,
            password=password, **kwargs)

    def login(self, retry=3):
        self._connection_prototype = FTPConnection
        return super(FTPSession, self).login(retry)

    @thread_lock
    def upload_file(self, local_file_path, remote_file_path=None):
        super(FTPSession, self).upload_file(local_file_path, remote_file_path)
        local_file_name = os.path.basename(local_file_path)
        remote_file_path = remote_file_path if remote_file_path else local_file_name
        self._session.storbinary('STOR {}'.format(remote_file_path), open(local_file_path))

    @thread_lock
    def download_file(self, remote_file_path, local_file_path=None):
        super(FTPSession, self).download_file(remote_file_path, local_file_path)
        remote_file_name = os.path.basename(remote_file_path)
        local_file_path = local_file_path if local_file_path else remote_file_name
        self._session.retrbinary('RETR {}'.format(remote_file_path), open(local_file_path, 'w').write)

    @ftp_command_execute
    def mkdir(self, path, mode=511):
        super(FTPSession, self).mkdir(path, mode)
        return self._session.mkd(path)

    @ftp_command_execute
    def rmdir(self, path):
        super(FTPSession, self).rmdir(path)
        return self._session.rmd(path)

    @ftp_command_execute
    def remove(self, path):
        super(FTPSession, self).remove(path)
        return self._session.delete(path)

    @ftp_command_execute
    def normalize(self, path):
        super(FTPSession, self).normalize(path)
        _tmp_dir = os.path.dirname(path)
        _tmp_name = os.path.basename(path)
        with self.context_chdir(_tmp_dir):
            _tmp_list = self.listdir()

            _tmp_dir = self.getcwd()
            if _tmp_name in _tmp_list:
                return os.path.join(_tmp_dir, _tmp_name).replace('\\', '/')
            raise FTPSessionException("Invalid path {}".format(path))

    @ftp_command_execute
    def listdir(self, path=''):
        super(FTPSession, self).listdir(path)
        return self._session.nlst(path)

    @ftp_command_execute
    def stat(self, path):
        super(FTPSession, self).stat(path)
        normal_path = self.normalize(path)

        dir_path = os.path.dirname(normal_path)
        base_name = os.path.basename(normal_path)

        attr = AttributeDict()

        def _callback(line):
            tmp_list = line.split()
            if tmp_list[-1] == base_name:
                attr.st_mode = tmp_list[0]
                attr.st_uid = tmp_list[2]
                attr.st_gid = tmp_list[3]
                attr.st_size = tmp_list[4]
                attr.st_atime = tmp_list[5:-1]
                attr.st_mtime = tmp_list[5:-1]

        self._session.retrlines("LIST %s" % dir_path, callback=_callback)

        return attr

    @ftp_command_execute
    def rename(self, oldpath, newpath):
        super(FTPSession, self).rename(oldpath, newpath)
        return self._session.rename(oldpath, newpath)

    @ftp_command_execute
    def getcwd(self):
        super(FTPSession, self).getcwd()
        return self._session.pwd()

    @ftp_command_execute
    def chdir(self, path):
        super(FTPSession, self).chdir(path)
        return self._session.cwd(path)


class FTPConnection(ftplib.FTP):
    def __init__(self, hostname, port=21, username='', password='', acct='', timeout=30, lock=None):
        self.port = port
        self.lock = lock
        ftplib.FTP.__init__(self, hostname, username, password, acct, timeout)


if __name__ == '__main__':
    client = FTPSession('192.168.33.10', username='test', password='test')

    res = client.listdir('../test/download')
    print res

    res = client.listdir('../test/download')
    print res
