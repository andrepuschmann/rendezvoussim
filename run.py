#!/usr/bin/env python
"""
Simulation of a various rendezvous algorithms
"""

import subprocess

#for i in (5,10):
for i in range(1,26):
    # run random algorithm, increase no of channels, two users
    subprocess.call(["./rendezvoussim2.py", "-a random", "-i 10000", "-q", "-n 2", "-c %d" % i])
    #subprocess.call(["./rendezvoussim2.py", "-a modularclock", "-i 10000", "-q", "-n 2", "-c %d" % i])
    #subprocess.call(["./rendezvoussim.py", "-a sequence", "-i 10000", "-t 10000", "-q", "-n 2", "-r 10", "-c %d" % i])

