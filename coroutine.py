# -*-coding: utf-8 -*-


def consumer():
    r = ''
    while True:
        # get message and return with r
        n = yield r
        if not n:
            print('not %d' % n)
            return
        print('[Consumer]Consume %d...' % n)
        r = '200 OK'


def producer(c):
    # start generator
    c.send(None)

    n = 1;
    while n < 5:
        print('[Producer]produce %d' % n)
        # swith to consumer to run
        r = c.send(n)
        n += 1
        print('[Producer]consume handle return %s' % r)

    c.close()

if __name__ == '__main__':
    c = consumer()
    producer(c)

# output
# [Producer]produce 1
# [Consumer]Consume 1...
# [Producer]consume handle return 200 OK
# [Producer]produce 2
# [Consumer]Consume 2...
# [Producer]consume handle return 200 OK
