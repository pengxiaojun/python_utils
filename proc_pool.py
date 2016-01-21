# -*-coding: utf-8 -*-


import os
import hashlib
import multiprocessing


BUFSIZE = 8192

POOLSIZE = 4


def add(x, y):
    return x + y


def print_result(result):
    print('Result is', result)


def compute_digest(file):
    try:
        f = open(file, 'rb')
    except IOError:
        return None

    digest = hashlib.sha512()
    while True:
        chunk = f.read(BUFSIZE)
        if not chunk:
            break
        digest.update(chunk)
    f.close()
    return file, digest.digest()


def build_digest_map(topdir):
    digest_pool = multiprocessing.Pool(POOLSIZE)
    allfiles = (os.path.join(path, name)
                for path, dirs, files in os.walk(topdir)
                for name in files)
    digest_map = dict(digest_pool.imap_unordered(compute_digest, allfiles, 20))
    digest_pool.close()
    return digest_map


if __name__ == '__main__':
    p1 = multiprocessing.Pool()
    print(p1.apply(add, (2, 3)))
    print(p1.apply(add, (4, 4)))

    p1.apply_async(add, (5, 5), callback=print_result)
    p1.close()
    p1.join()

    # compute digest
    digest_map = build_digest_map('.')
    print(digest_map)
    print(len(digest_map))
