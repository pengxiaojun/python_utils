# -*-coding: utf-8 -*-


import sys
import asyncio

HOST='127.0.0.1'
PORT=9090

clients = set()


def server_handle_client(reader, writer):
    print('Enter client handler')
    self_client = (reader, writer)
    clients.add(self_client)

    while True:

        data = yield from reader.readline()

        if not data:
            clients.remove(self_client)
            print('-> Client removed (%d))' % len(clients))
            break

        print('-> Message received %s' % data.decode())

        for client in clients:
            if client != self_client:
                client[1].write(data)


@asyncio.coroutine
def server_start():
    yield from asyncio.start_server(server_handle_client, host=HOST, port=PORT)



@asyncio.coroutine
def client_read_message(reader):
    while True:
        data = yield from reader.readline()

        if not data:
            break
        print(data.decode(), end='')


@asyncio.coroutine
def client_write_message(writer, disconnfut):
    stdin_reader = asyncio.StreamReader(loop=loop)

    yield from loop.connect_read_pipe(
        lambda: asyncio.StreamReaderProtocol(stdin_reader),
        sys.stdin
    )

    while True:
        input_data = yield from stdin_reader.readline()

        if input_data[0:4] == b'quit':
            disconnfut.set_result(True)
            break

        writer.write(input_data)
        yield from writer.drain()


@asyncio.coroutine
def client_say_goodbye(writer):
    writer.write(b'Bye\n')


@asyncio.coroutine
def client_start():
    reader, writer = yield from asyncio.open_connection(host=HOST, port=PORT)
    return (reader, writer)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: %s [--server | --client]' % sys.argv[0])
        sys.exit()


    if sys.argv[1] == '--server':
        loop = asyncio.get_event_loop()
        loop.run_until_complete(server_start())
        loop.run_forever()
    else:
        loop = asyncio.get_event_loop()
        disconnfut = asyncio.Future()
        r, w = loop.run_until_complete(client_start())
        asyncio.async(client_read_message(r))
        asyncio.async(client_write_message(w, disconnfut))
        disconnfut.add_done_callback(lambda fut: client_say_goodbye(w))
        loop.run_until_complete(disconnfut)
