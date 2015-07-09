# -*-coding: utf-8 -*-


import os
import socket
import ctypes
import struct
import threading
import netaddr
import time


HOST = '192.168.1.25'
SUBNET = '192.168.1.0/24'
MESSAGE = 'ooooooops'


def udp_sender(SUBNET, MESSAGE):
    time.sleep(5)
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for ip in netaddr.IPNetwork(SUBNET):
        try:
            print('send to %s' % ip)
            sender.sendto(MESSAGE, ("%s" % ip, 65212))
        except:
            pass


class ICMP(ctypes.Structure):
    _fields_ = [
        ('type', ctypes.c_ubyte),
        ('code', ctypes.c_ubyte),
        ('checksum', ctypes.c_ushort),
        ('unused', ctypes.c_ushort),
        ('next_hop_mtu', ctypes.c_ushort)
    ]

    def __new__(self, socket_buffer):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer):
        pass


def sniffing(host, win, socket_prot):
    thread = threading.Thread(target=udp_sender, args=(SUBNET, MESSAGE))
    thread.start()

    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_prot)
    sniffer.bind((host, 0))
    # include ip header in capture structure
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    while 1:
        raw_buffer = sniffer.recvfrom(65565)[0]
        ip_header = raw_buffer[0:20]
        iph = struct.unpack('!BBHHHBBH4s4s', ip_header)

        # create our ip structure
        version_ihl = iph[0]
        version = version_ihl >> 4
        ihl = version_ihl & 0x0F
        iph_length = ihl * 4
        ttl = iph[5]
        protocol = iph[6]
        s_addr = socket.inet_ntoa(iph[8])
        d_addr = socket.inet_ntoa(iph[9])

        print('IP -> version:', version, ',Header length:', ihl,
              ', TTL:', ttl, ',Protocol', protocol,
              ', Source:', s_addr, ', Destination', d_addr)

        # create our ICMP structure
        buf = raw_buffer[iph_length:iph_length + ctypes.sizeof(ICMP)]
        icmp_header = ICMP(buf)

        print("ICMP->Type:%d, Code:%d" % (icmp_header.type, icmp_header.code))

        if (icmp_header.type == 3 and icmp_header.code == 3):
            if (netaddr.IPAddress(s_addr) in netaddr.IPNetwork(SUBNET)):
                if (raw_buffer[len(raw_buffer)-len(MESSAGE):] == MESSAGE):
                    print ("Host up: %s" % s_addr)


def main(host):
    if (os.name == "nt"):
        sniffing(host, 1, socket.IPPROTO_IP)
    else:
        sniffing(host, 0, socket.IPPROTO_ICMP)


if __name__ == '__main__':
    main(HOST)
