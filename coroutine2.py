# -*-coding: utf-8 -*-


def coroutine(func):
    def start(*args, **kwargs):
        g = func(*args, **kwargs)
        next(g)  # or g.__next__()
        return g
    return start


@coroutine
def print_matches(matchtext):
    print('Looking for', matchtext)

    while True:
        line = (yield)

        if matchtext in line:
            print(line)

if __name__ == '__main__':
    match = print_matches('python')
    match.send('hello')
    match.send('div to python')
