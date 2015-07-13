# -*-coding: utf-8 -*-


class MyDict(dict):

    def __init__(self, **kv):
        super().__init__(**kv)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError("object has no attribute '%s'" % key)

    def __setattr__(self, k, v):
        self[k] = v


import unittest


class TestMyDict(unittest.TestCase):
    def test_init(self):
        d = MyDict(a=1, b=True)
        self.assertEqual(d.a, 1)
        self.assertTrue(d.b, True)


if __name__ == '__main__':
    unittest.main()
