# -*-coding: utf-8 -*-


import time


class Date(object):
    def __init__(self, y, m, d):
        self.year = y
        self.month = m
        self.day = d

    # @staticmethod
    @classmethod
    def now(cls):
        t = time.localtime()
        return cls(t.tm_year, t.tm_mon, t.tm_mday)

    # @staticmethod
    @classmethod
    def tomorrow(cls):
        t = time.localtime()+86400
        return cls(t.tm_year, t.tm_mon, t.tm_mday)

    @property
    def format(self):
        return 'yyyy/MM/dd'

    @format.getter
    def format(self):
        return 'aa'

    @format.setter
    def format(self, value):
        if not isinstance(value, str):
            raise TypeError('Must be a string')

    @format.deleter
    def format(self):
        raise TypeError('Can not delete me')


class EuroDate(Date):
    def __str__(self):
        return '%02d/%02d/%04d' % (self.month, self.day, self.year)
