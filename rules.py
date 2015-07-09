# -*-coding: utf-8 -*-

import re


class LazyRules:
    rule_pattern_file = "rules.txt"

    def __init__(self):
        self.pattern_file = open(self.rule_pattern_file, "r", encoding='utf-8')
        self.cache = []

    def __iter__(self):
        self.cache_index = 0
        return self

    def build_match_and_apply_functions(self, pattern, search, sub):
        def match_rule(word):
            return re.search(pattern, word)

        def apply_rule(word):
            return re.sub(search, sub, word)
        return (match_rule, apply_rule)

    def __next__(self):
        if (len(self.cache) > self.cache_index):
            return self.cache[self.cache_index]

        self.cache_index += 1

        if (self.pattern_file.closed):
            raise StopIteration

        line = self.pattern_file.readline()
        if not line:
            self.pattern_file.close()
            raise StopIteration

        pattern, search, sub = line.split(None, 3)
        func = self.build_match_and_apply_functions(pattern, search, sub)
        self.cache.append(func)
        return func

if __name__ == '__main__':
    for rule in LazyRules():
        print(rule)
