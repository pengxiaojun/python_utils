# -*-coding: utf-8 -*-


import os
from collections import deque


class Scheduler:
    def __init__(self):
        self.tasks = deque()

    def schedule(self, task):
        self.tasks.append(task)

    def run(self):
        while self.tasks:
            task = self.tasks.popleft()

            try:
                task.run()
            except StopIteration:
                print('Task %s has finished' % task)
            else:
                self.tasks.append(task)


class Task:

    ID = 0

    def __init__(self, runner):
        Task.ID += 1
        self.id = Task.ID
        self.runner = runner

    def __str__(self):
        return str(self.id)

    def run(self):
        result = next(self.runner)
        print('[%d] %s' % (self.id, result))


def list_dir(path):
    for item in os.listdir(path):
        yield item


def echo_text(times):
    for i in range(times):
        yield 'Hi,dude'


if __name__ == '__main__':
    s = Scheduler()

    s.schedule(Task(list_dir('.')))
    s.schedule(Task(echo_text(5)))
    s.schedule(Task(echo_text(2)))

    s.run()
