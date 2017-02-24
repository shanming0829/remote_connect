from contextlib import contextmanager
import os


@contextmanager
def switch_sock_read_timeout(sock, timeout):
    old_timeout = sock.gettimeout()
    sock.settimeout(timeout)
    yield
    sock.settimeout(old_timeout)


@contextmanager
def local_change_dir(path):
    current_pwd = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(current_pwd)


@contextmanager
def thread_acquire_and_release(lock):
    lock.acquire()
    yield
    lock.release()
