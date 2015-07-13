# -*-coding: utf-8 -*-


import socket


def client():
    sfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sfd.connect(('127.0.0.1', 8899))
    print("connect to 8899")

    for data in [b'Michael', b'Bob', b'Tom']:
        sfd.send(data)
        print('send', data)

    sfd.send(b'exit')
    sfd.close()

if __name__ == '__main__':
    client()
