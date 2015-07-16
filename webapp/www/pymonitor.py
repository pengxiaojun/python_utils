#!/usr/bin/env python3
# -*-coding: utf-8 -*-


import os
import time
import subprocess
import sys

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


def log(s):
    print('[Monitor] %s' % s)


class MyFileSystemHandler(FileSystemEventHandler):
    '''
    watch python source file
    '''

    def __init__(self, fn):
        super(MyFileSystemHandler, self).__init__()
        self.restart = fn

    def on_any_event(self, event):
        log('recv event %s' % event.src_path)
        if event.src_path.endswith('.py'):
            log('Python source file %s changed' % event.src_path)
        self.restart()


command = ['echo', 'ok']
process = None


def kill_process():
    global process
    if process:
        log('kill process %s...' % process.pid)
        process.kill()
        process.wait()
        log('process end with code %s' % process.returncode)


def start_process():
    global process, command
    log('start process %s' % ' '.join(command))
    process = subprocess.Popen(command,
                               stdin=sys.stdin,
                               stdout=sys.stdout,
                               stderr=sys.stderr)


def restart_process():
    kill_process()
    start_process()


def start_watch(path, callback):
    observer = Observer()
    observer.schedule(MyFileSystemHandler(restart_process),
                      path,
                      recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':
    argv = sys.argv[1:]
    if not argv:
        print('Usage: ./pymonitor your-script.py')
        exit(0)
    if argv[0] != 'python':
        argv.insert(0, 'python')
    command = argv
    path = os.path.abspath('.')
    print(argv, path)
    start_watch(path, None)
