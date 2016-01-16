# -*-coding: utf-8 -*-


import os

def coroutine(func):
    def start(*args, **kwargs):
        g = func(*args, **kwargs)
        next(g)
        return g

    return start


@coroutine
def find_files(target):
    while True:
        dir, pattern = (yield)
        for path, dirnames, files in os.walk(dir):
            for f in files:
                if pattern in f:
                    target.send(os.path.join(path, f))


@coroutine
def opener(target):
    while True:
        filename = (yield)
        with open(filename) as f:
            target.send(f)


@coroutine
def cat(target):
    while True:
        f = (yield)
        for line in f:
            target.send(line)


@coroutine
def grep(pattern, target):
    while True:
        line = (yield)

        if pattern in line:
            target.send(line)


@coroutine
def printer():
    while True:
        line = (yield)
        print(line, end='')


if __name__ == '__main__':
    f = find_files(opener(cat(grep('python', printer()))))
    f.send(('.', '.log'))
