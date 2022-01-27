#!/usr/bin/env python3

import sys

import pandas as pd

infile = sys.argv[1]

with open(infile) as f:
    times = f.readlines()

n = len(times) - 1

flat_list = [item for sublist in [x.strip().split(",") for x in times[1:]] for item in sublist]

pd_times = pd.to_datetime(flat_list)
pd_starts = pd_times[::2]
pd_ends = pd_times[1::2]

clashes = []
for i in range(n - 1):
    for j in range(i + 1, n):
        lastest_start = max(pd_starts[i], pd_starts[j])
        earliest_end = min(pd_ends[i], pd_ends[j])
        if earliest_end > lastest_start:  # we have a clash
            delta = earliest_end - lastest_start
            clashes.append((i, j, delta.seconds // 60, lastest_start.strftime("%H:%M"), earliest_end.strftime("%H:%M")))

for row in clashes:
    m1, m2, mtime, begin, end = row
    print(f"Meetings: <{m1+1}> and <{m2+1}> overlaps for {mtime} minutes (between {begin} and {end})")
