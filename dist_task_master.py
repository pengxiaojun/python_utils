# -*-coding: utf-8 -*-


from multiprocessing.managers import BaseManager
import random
import queue


class QueueManager(BaseManager):
    pass


task_q = queue.Queue()
result_q = queue.Queue()


if __name__ == '__main__':
    # register task and result queue
    QueueManager.register('get_task_q', callable=lambda: task_q)
    QueueManager.register('get_result_q', callable=lambda: result_q)

    # bind maanger to port
    manager = QueueManager(address=('', 5000), authkey=b'key')
    # start queue
    manager.start()
    # get queue can accessable by network
    task = manager.get_task_q()
    result = manager.get_result_q()
    # push some task
    for i in range(10):
        n = random.randint(0, 10000)
        task.put(n)
        print("task push %d" % n)

    # get result
    print("Try get result")
    for i in range(10):
        r = result.get(timeout=10)
        print("get result %s" % r)

    # shutdown
    manager.shutdown()
    print("master exit")
