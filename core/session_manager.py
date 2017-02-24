from sessions import TelnetSession, SSHSession, FTPSession, SFTPSession
from core.log.log import Logger


class SessionManagerException(Exception):
    pass


class SessionManagerWarning(Warning):
    pass


class _SessionManager(object):
    Protocols = {'TELNET': TelnetSession, 'SSH': SSHSession, 'FTP': FTPSession, 'SFTP': SFTPSession}

    def __init__(self, config, logger=None):
        self.config = config

        self.logger = logger if logger is not None else Logger('session_manager')

    def create_sessions(self):
        sessions = dict()
        for name in self.config.keys():
            sessions[name] = self.get_session(name)

        return sessions

    def _create_session(self, session_name, protocol_type):
        self.logger.debug('Create session {}, session type {}'.format(session_name, str(protocol_type)))

        session_config = self.config[session_name]

        return protocol_type(logger=self.logger.getChild(session_name), **session_config)

    def _check_session_type(self, session_name, session_config):
        port = session_config.get('port', None)
        protocol = session_config.get('protocol', None)

        if protocol is None and port is None:
            raise SessionManagerException(
                "Create session {} failed, config must contain protocol or port".format(session_name))
        elif protocol:
            if protocol.upper() in self.Protocols:
                return self.Protocols[protocol.upper()]
            else:
                raise SessionManagerWarning(
                    "Create session {} failed, protocol currently not support yet".format(session_name))
        elif port:
            if port == 21:
                return self.Protocols['TELNET']
            elif port == 22:
                return self.Protocols['SSh']
            elif port == 23:
                return self.Protocols['FTP']
            else:
                raise SessionManagerException(
                    "Create session {} failed, given port is not regular, please given protocol".format(session_name))

    def get_session(self, session_name):
        session_config = self.config.get(session_name, None)
        if not session_config:
            raise SessionManagerWarning("Create session {} failed, no detail info for session".format(session_name))

        protocol_type = self._check_session_type(session_name, session_config)

        return self._create_session(session_name, protocol_type)


SessionManager = _SessionManager
