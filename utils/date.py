# -*- coding: utf-8 -*-

from collections import namedtuple

Range = namedtuple('Range', ['start', 'end'])


# 傳回兩個 range 重疊的天數
def range_overlap(rangeA, rangeB):
    latest_start = max(rangeA.start, rangeB.start)
    earliest_end = min(rangeA.end, rangeB.end)
    delta = (earliest_end - latest_start).days + 1
    overlap = max(0, delta)
    return overlap
