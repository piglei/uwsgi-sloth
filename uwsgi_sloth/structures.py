# -*- coding: utf-8 -*-
"""Useful data structures"""


class ValuesAggregation(object):
    """For response time analyze"""

    def __init__(self, values=[]):
        self.min = None
        self.max = None
        self.total = 0
        self.count = 0
        # Init with values
        for value in values:
            self.add_value(value)

    def add_value(self, value):
        self.count += 1
        self.total += value
        if self.max is None or value > self.max:
            self.max = value
        if self.min is None or value < self.min:
            self.min = value

    def add_values(self, values):
        for value in values:
            self.add_value(value)

    @property
    def avg(self):
        if not self.count:
            return 0
        return self.total / float(self.count)

    def merge_with(self, other):
        """Merge this ``ValuesAggregation`` with another one"""
        result = ValuesAggregation()
        result.total = self.total + other.total
        result.count = self.count + other.count
        result.min = min(self.min, other.min)
        result.max = max(self.max, other.max)
        return result

    def get_result(self):
        return {
            'min': self.min,
            'max': self.max,
            'avg': self.avg,
        }

