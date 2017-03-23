# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import time
import random
from collections import namedtuple
from multiprocessing import Pool, Process, current_process, Manager
from concurrent.futures import ProcessPoolExecutor

__authors__ = "Shanming Liu"


def plus(a, b):
    sleep_time = random.random()
    print('time sleep -> {}'.format(sleep_time))
    time.sleep(sleep_time)
    print('current process -> {}'.format(str(current_process())))
    return a + b


def test_pool():
    pool = Pool(2)

    for a, b in zip(range(10), range(11, 20)):
        pool.apply_async(plus, args=(a, b))

    pool.close()
    pool.join()


def test_concurrent():
    pool = ProcessPoolExecutor(2)

    for a, b in zip(range(10), range(11, 20)):
        pool.submit(plus, a, b)

    pool.shutdown()


# Position = namedtuple('Position', field_names=('x', 'y'))

class Position(object):
    def __init__(self, x=10, y=10):
        self.x = x
        self.y = y


def change_position(d):
    # print(id(d))
    source_dict = d

    source_dict['position'].x = 100
    source_dict['position'].y = 100
    source_dict['a'] = 10
    # print(id(source_dict['position']))


def test_manager():
    position = Position(x=10, y=10)

    # print(id(position))

    manager = Manager()

    d = manager.dict(position=position)
    # print(id(d))

    process = Process(target=change_position, name='change', args=(d,))
    process.start()
    process.join()

    print d['position'].__dict__


def sys_out(value):
    print(value)
    time.sleep(random.random())


def test_pool_reuse():
    pool = Pool(2)
    for i in range(10):
        pool.apply_async(sys_out, args=('sys out',))
    pool.close()
    pool.join()

    for i in range(10):
        pool.apply_async(sys_out, args=('print out',))
    pool.close()
    pool.join()


def exception_func():
    print('aaa')
    raise AttributeError('No attribute')


def test_exception():
    pool = Pool(2)
    result = pool.apply_async(exception_func, )

    pool.close()
    pool.join()

    result.get()


if __name__ == '__main__':
    test_exception()
