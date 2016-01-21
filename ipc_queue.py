# -*-coding: utf-8 -*-


import multiprocessing


def consumer(input_q):
    while True:
        item = input_q.get()
        if not item:
            break
        print(item)
        input_q.task_done()


def producer(sequence, output_q):
    for item in sequence:
        output_q.put(item)


if __name__ == '__main__':
    q = multiprocessing.JoinableQueue()
    cons_p = multiprocessing.Process(target=consumer, args=(q,))
    cons_p.daemon = True
    cons_p.start()

    cons_p1 = multiprocessing.Process(target=consumer, args=(q,))
    cons_p1.daemon = True
    cons_p1.start()

    sequence = [1, 2, 3, 4]
    producer(sequence, q)
    q.join()
