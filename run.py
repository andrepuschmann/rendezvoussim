#!/usr/bin/env python
"""
Simulation of a various rendezvous algorithms
"""

import subprocess

#for i in (5,10):
#for i in range(1,26):
    # run random algorithm, increase no of channels, two users
    #subprocess.call(["./rendezvoussim2.py", "-a random", "-i 10000", "-q", "-n 2", "-c %d" % i])
    #subprocess.call(["./rendezvoussim2.py", "-a modularclock", "-i 10000", "-q", "-n 2", "-c %d" % i])
    #subprocess.call(["./rendezvoussim.py", "-a sequence", "-i 10000", "-t 10000", "-q", "-n 2", "-r 10", "-c %d" % i])
    #subprocess.call(["./rendezvoussim2.py", "-a jumpstay", "-i 10000", "-q", "-n 2", "-c %d" % i])

# for increasing G (number of overlapping channels) evaluate algorithms with fixed number of channels (c=20)
for i in range(2,21):
    #subprocess.call(["./rendezvoussim2.py", "-c 20", "-a random", "-i 10000", "-m", "async", "-q", "-n 2", "-g %d" % i])
    subprocess.call(["./rendezvoussim2.py", "-c 40", "-a jumpstay", "-i 1000", "-m", "async", "-q", "-n 2", "-g %d" % i])
