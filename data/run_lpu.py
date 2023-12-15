#!/usr/bin/env python

"""
Run timing test (non-GPU) scaled over number of LPUs.
"""

import csv
import multiprocessing as mp
import re
import subprocess
import sys

import numpy as np

from neurokernel.tools.misc import get_pids_open

try:
    from subprocess import DEVNULL
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')

out_file = sys.argv[1]
script_name = 'timing_demo.py'
trials = 3

def check_and_print_output(*args):
    while True:
        try:
            out = subprocess.check_output(args[0], env=os.environ, 
stderr=DEVNULL)
        except Exception as e:
            pass
        else:
            break
    row = out.strip('[]\n\"').split(', ')
    row[1] = str(args[1])
    out = ','.join(row)
    print out
    return out

pool = mp.Pool(1)
results = []
for spikes in xrange(250, 7000, 250):
    for lpus in xrange(2, 9):
        for i in xrange(trials):
            r = pool.apply_async(check_and_print_output,
                                 [['srun', '-n', '1', '-c', str(lpus),
                                   '-p', 'huxley',
                                   'python', script_name,
                                   '-u', str(lpus), '-s', 
str(spikes/(lpus-1)),
                                   '-g', '0', '-m', '50'], spikes])
            results.append(r)
f = open(out_file, 'w', 0)
w = csv.writer(f)
for r in results:

    # Include total number of spikes rather than per-LPU number of spikes 
in output:
    row = r.get().strip('[]\n\"').split(',')
    w.writerow(row)
f.close()
