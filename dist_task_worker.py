# -*-coding: utf-8 -*-


import queue
from multiprocessing.managers import BaseManager


class QueueManager(BaseManager):
    pass


if __name__ == '__main__':
    # only register queue
    QueueManager.register('get_task_q')
    QueueManager.register('get_result_q')

    server_address = '192.168.1.25'
    manager = QueueManager(address=(server_address, 5000), authkey=b'key')

    manager.connect()

    task = manager.get_task_q()
    result = manager.get_result_q()

    for i in range(10):
        try:
            n = task.get(timeout=1)
            print("get task %d" % n)
            r = '%d * %d = %d' % (n, n, n*n)
            result.put(r)
            print("put result %s" % r)
        except queue.Queue.Empty:
            print("task queue is empty")
    print("worker exit")
