# -*-coding: utf-8 -*-


import threading


q = []


def producer(cv):
    for i in [1, 2, 3, 4, None]:
        cv.acquire()
        q.append(i)
        print('Produce', i)
        cv.notify()
        cv.release()


def consumer(cv):
    while True:
        cv.acquire()
        while len(q) == 0:
            cv.wait()
        item = q.pop(0)
        print('Consume', item)
        cv.release()
        if not item:
            break

if __name__ == '__main__':
    cv = threading.Condition()
    cons_thread = threading.Thread(target=consumer, args=(cv,))
    prod_thread = threading.Thread(target=producer, args=(cv,))

    cons_thread.start()
    prod_thread.start()

    cons_thread.join()
    prod_thread.join()
