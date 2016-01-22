# -*-coding: utf-8 -*-


import types


def from_pyfile(filename):
    d = types.ModuleType('config')
    d.__file__ = filename
    d.__doc__ = 'doc'
    with open(filename) as config_file:
        exec(compile(config_file.read(), filename, 'exec'), d.__dict__)

    return d

if __name__ == '__main__':
    d = from_pyfile('a.cfg')
    print(d)
    for key in dir(d):
        print(key, getattr(d, key))
