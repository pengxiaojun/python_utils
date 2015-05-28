# -*- coding: utf-8 -*-

unit_size = {
    1024: ['KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB'],
    1000: ['KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
}


def humansize(size, kib=True):
    """ Convert size to hunam-readable form

    argements:
    size --size in bytes
    kib --if True(default), use multiples of 1024.
          else use mutilples of 1000
    returns: string

    """
    if (size < 0):
        raise ValueError("Only non-negtive number supported!")

    multiple = 1024 if kib else 1000

    if size < multiple:
        return "{0:.1f}Byte(s)".format(size)

    for unit in unit_size[multiple]:
        size /= multiple
        if size < multiple:
            return "{0:.1f}{1}".format(size, unit)

    raise ValueError("Huge number not supported!")


if __name__ == '__main__':
    # print(humansize(-1))  # negtive number
    print(humansize(50))  # bytes
    print(humansize(2487))  # kb
    print(humansize(4096922))  # mb
    print(humansize(4096000000))  # gb
    print(humansize(8192945817239))  # tb
    print(humansize(7654212333944444))  # pb
    print(humansize(9876654335122299878))  # eb
    print(humansize(5623399166033343827409))  # zb
    print(humansize(3438173048374837413421834))  # yb
    # print(humansize(2938439283102341823492342134))  # huge number
