# -*-coding: utf-8 -*-

import os
import coroutine


def consumer():
    r = ''
    while True:
        # get message and return with r
        n = yield r
        if not n:
            print('not %d' % n)
            return
        print('[Consumer]Consume %d...' % n)
        r = '200 OK'


def producer(c):
    # start generator
    c.send(None)

    n = 1;
    while n < 5:
        print('[Producer]produce %d' % n)
        # swith to consumer to run
        r = c.send(n)
        n += 1
        print('[Producer]consume handle return %s' % r)

    c.close()


def list_dir(path, target):
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            print('list send', filename)
            target.send(filename)


def coroutine(func):
    def wrapper(*args, **kwargs):
        gen = func(*args, **kwargs)
        print(func.__name__, 'next begin')
        next(gen)
        print(func.__name__, 'next end')
        return gen

    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__ = func.__doc__

    return wrapper


@coroutine
def filter_str(pattern, target):
    while True:
        print('filter begin')
        filename = (yield)
        if pattern in filename:
            print('filter send %s' % filename)
            target.send(filename)
            print('filter send done')


@coroutine
def print_match():
    while True:
        print('print begin')
        result = (yield)
        print(result)
        print('print end', result)


if __name__ == '__main__':
    c = consumer()
    producer(c)
    list_dir('.', filter_str('.txt', print_match()))

# output
# [Producer]produce 1
# [Consumer]Consume 1...
# [Producer]consume handle return 200 OK
# [Producer]produce 2
# [Consumer]Consume 2...
# [Producer]consume handle return 200 OK
