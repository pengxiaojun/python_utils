# -*-coding: utf-8 -*-


import asyncio
from aiohttp import web


def index(request):
    return web.Response(body=b'<h1>index</h1>')


def hello(request):
    yield from asyncio.sleep(1)
    text = '<h1>hello,%s</h1>' % request.match_info['user']
    return web.Response(body=text.encode('utf-8'))


@asyncio.coroutine
def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', index)
    app.router.add_route('GET', '/hello/{user}', hello)
    srv = yield from loop.create_server(app.make_handler(), '0.0.0.0', 8000)
    return srv


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop))
    loop.run_forever()
