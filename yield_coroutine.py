# -*-coding: utf-8 -*-


import os


def find_files(dir, pattern):
    for path, dirnames, filelist in os.walk(dir):
        for f in filelist:
            if pattern in f and '.pyc' not in f:
                yield os.path.join(path, f)


def opener(files):
    for file in files:
        with open(file) as f:
            yield f


def cat(files):
    for f in files:
        for line in f:
            yield line


def grep(lines, pattern):
    for line in lines:
        if pattern in line:
            yield line


if __name__ == '__main__':
    files = find_files('.', '.py')
    files = opener(files)
    lines = cat(files)
    pylines = grep(lines, 'python')
    for line in pylines:
        print(line)
