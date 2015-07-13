# -*-coding: utf-8 -*-


import socket
import time
import threading


def handle_client(sfd, addr):
    while True:
        data = sfd.recv(1024)
        time.sleep(1)
        print("recv", data.decode('utf-8'))
        if not data or data.decode('utf-8') == 'exit':
            break
        sfd.send(('Hello,%s!' % data).encode('utf-8'))
    sfd.close()
    print("client %s:%s close" % addr)


if __name__ == '__main__':
    sfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sfd.bind(('127.0.0.1', 8899))
    sfd.listen(1024)

    while True:
        sock, addr = sfd.accept()
        t = threading.Thread(target=handle_client, args=(sock, addr))
        t.start()
