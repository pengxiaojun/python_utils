# -*-coding: utf-8 -*-


import multiprocessing
import os
import time
import random
import subprocess
import threading


def run_test(name):
    print("subprocess %s is running. pid=%d" % (name, os.getpid()))


def long_time_task(i):
    print("running task%d pid=%d" % (i, os.getpid()))
    start = time.time()
    time.sleep(random.random() * 3)
    stop = time.time()
    print("task%d elapsed %d" % (i, stop - start))
    time.sleep(random.random() * 5)


def write(q):
    print("Process %d write to queue" % os.getpid())
    for s in ['A', 'B', 'C', 'D']:
        q.put(s)
        print("put %s to queue" % s)


def read(q):
    print("Process %d read frorm queue" % os.getpid())
    while True:
        s = q.get()
        print("get %s from queue" % s)


def loop():
    x = 1
    while True:
        x ^= 1


local_var = threading.local()


def process_stud():
    stu = local_var.student
    print("thread:%s hello, %s" % (threading.current_thread().name, stu))


def threadlocal_task(arg):
    local_var.student = arg
    print("thread:%s set student %s" % (threading.currentThread().name, arg))
    process_stud()


if __name__ == '__main__':
    # GIL only one core reach to 100% when run in multiple core cpu
    # for i in range(multiprocessing.cpu_count()):
    #    t = threading.Thread(target=loop)
    #    t.start()

    print("Parent process pid is %d" % os.getpid())
    p = multiprocessing.Process(target=run_test, args=('test',))
    print("child will start")
    p.start()
    p.join()
    print("end")

    p = multiprocessing.Pool(4)
    for i in range(5):
        p.apply_async(long_time_task, args=(i,))
    p.close()
    p.join()
    print("all process done")
    # subprocess.call(['nslookup', 'www.python.org'])
    p = subprocess.Popen(['nslookup'], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    output, err = p.communicate(b'set q=mx\npython.org\nexit\n')
    print(output.decode('utf-8'))
    print("Exit code:", p.returncode)

    # IPC
    q = multiprocessing.Queue()
    p1 = multiprocessing.Process(target=write, args=(q,))
    p2 = multiprocessing.Process(target=read, args=(q,))

    p1.start()
    p2.start()
    p2.terminate()
    p1.join()
    print("all done")

    # thread local
    t1 = threading.Thread(target=threadlocal_task, args=('Bob',))
    t2 = threading.Thread(target=threadlocal_task, args=('Tom',))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
