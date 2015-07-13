# -*-coding: utf-8 -*-


import asyncio
import threading


@asyncio.coroutine
def hello():
    print('hello %s' % threading.currentThread())
    r = yield from asyncio.sleep(5)
    print('hello again %s' % threading.currentThread())


@asyncio.coroutine
def wget(host):
    print('wget %s' % host)
    conn = asyncio.open_connection(host, 80)
    reader, writer = yield from conn
    header = 'GET / HTTP/1.0 \r\nHost: %s\r\n\r\n' % host
    writer.write(header.encode('utf-8'))
    yield from writer.drain()
    while True:
        line = yield from reader.readline()
        if line == b'\r\n':
            break
        print('%s header > %s' % (host, line.decode('utf-8').rstrip()))
    writer.close()


loop = asyncio.get_event_loop()
tasks = [hello(), hello()]
tasks2 = [wget(s) for s in ['www.sohu.com', 'www.163.com', 'www.sina.com']]
loop.run_until_complete(asyncio.wait(tasks2))
loop.close()
