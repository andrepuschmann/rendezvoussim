#!/usr/bin/env python
"""
Simulation of a various rendezvous algorithms
"""
import sys
import matplotlib.pyplot as plt
import numpy as np
import pylab as P
from random import Random,expovariate,uniform
from algorithms import *
from optparse import OptionParser

RANDOM_SEED = 42
MAX_SLOTS = 9999

class MinMaxMonitor():
    def __init__(self):
        self.values = []
    def tally(self, x):
        self.values.append(x)
    def mean(self):
        return np.mean(self.values)
    def min(self):
        return np.min(self.values)
    def max(self):
        return np.max(self.values)
    def len(self):
        return len(self.values)
    def var(self):
        return np.var(self.values)
    def std(self):
        return np.std(self.values)
    def reset(self):
        self.values = []
        

class Channel():
    def __init__(self, name='Default channel'):
        self.name = name
        
    def getName(self):
        return self.name

class Node():
    def __init__(self, name='Default node', algorithm=None, channels=None, verbose=True):
        self.name = name
        self.channels = channels
        self.no_channels = len(channels)
        self.verbose = verbose
        if "random" in algorithm:
            self.algorithm = RandomRendezvous(self.no_channels, verbose)
        elif "sequence" in algorithm:
            self.algorithm = SequenceRendezvous(self.no_channels, False)
            #self.algorithm = SequenceRendezvous(self.no_channels, True)
            self.algorithm.printSequence()
        elif "modularclock" in algorithm:
            self.algorithm = ModularClockRendezvous(self.no_channels, verbose)
        elif "jumpstay" in algorithm:
            self.algorithm = JSHoppingRendezvous(self.no_channels, verbose)
        else:
            print "Rendezvous algorithm %s is not supported." % (algorithm)
            sys.exit()        

        self.printChannels()

    def printChannels(self):
        self.trace(0, "My channels: %d" % len(self.channels))
        for i in self.channels:
            self.trace(message="  %s" % i.getName())


    def getNextChannel(self, slot):
        self.trace(slot, "Determine next channel ...")
        r = self.algorithm.getNextIndex()
        self.trace(slot, "Next channel has index %d" % (r))
        # check validity
        if r > (self.no_channels - 1):
            print "Error, too large channel index"
            sys.exit()
        return self.channels[r]
        
    def trace(self, slot=0, message=''):
        if self.verbose: print "%d: %s:\t%s" % (slot, self.name, message)
        

def isEqual(iterator):
      try:
         iterator = iter(iterator)
         first = next(iterator)
         return all(first == rest for rest in iterator)
      except StopIteration:
         return True


def createEnvironment(model, num_channels, num_overlap_channels, theta, num_nodes, algorithm, verbose):
    nodes = []
    
    # Create the channels and nodes
    if model == "sync":
        channels = []
        # All nodes have all channels in common
        for i in range(num_channels):
            channels.append(Channel('Channel %d' % i))
        for n in range(num_nodes):
            nodes.append(Node('Node %d' % n, algorithm, channels, verbose))
        # debug
        #for i in channels:
        #    print "%s" % i.name

    elif model == "async":
        common_channels = []
        created_channels = 0
        # Create common channels first
        for i in range(num_overlap_channels):
            common_channels.append(Channel('Channel %d' % created_channels))
            created_channels += 1
      
        # Create individual channels for each user
        for n in range(num_nodes):
            channels = []
            channels += common_channels # start with common channels first
            # create remaining channels
            num_nonoverlap_channels = num_channels - num_overlap_channels
            # in Liu's paper, a theta paper has been defined that determines the actual number of channels
            if theta < 1.0:
                r = np.random.normal(theta, 0.1) # draw random variable from a normal distribution with a mean of theta and std dev 0.1
                num_nonoverlap_channels = int(num_nonoverlap_channels * r)
            #print "num_nonoverlap_channels: %d" % num_nonoverlap_channels
            for i in range(num_nonoverlap_channels):
                channels.append(Channel('Channel %d' % created_channels))
                created_channels += 1
                
            # some debug output
            #print "Node %d has %d channels." % (n, len(channels))
            # finally create node 
            nodes.append(Node('Node %d' % n, algorithm, channels, verbose))
            
        #print "num_channels: %d" % num_channels
        #print "num_overlap_channels: %d" % num_overlap_channels
        #print "Created channels: %d" % created_channels

    return nodes


def main():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("-a", "--algorithm", dest="algorithm", default="random",
                      help="Which rendezvous algorithm to simulate")
    parser.add_option("-c", "--channels", dest="channels", default=5,
                      help="How many channels are available")
    parser.add_option("-m", "--model", dest="model", default="sync",
                      help="Which channel model to use (sync or async)")
    parser.add_option("-g", "--overlapping channels", dest="overlap_channels", type="int", default="5",
                      help="How many channels are overlapping between nodes (only for async model)")

    parser.add_option("-t", "--theta-parameter", dest="theta", type="float", default="1.0",
                      help="The theta parameter defined in Liu's paper. It is multiplied with M to determine the actual number of channels")

    parser.add_option("-n", "--nodes", dest="nodes", default=2,
                      help="How many nodes are used")
    parser.add_option("-i", "--iterations", dest="iterations", default=1,
                      help="How often to repeat the simulation")
    parser.add_option("-u", "--tune", dest="tunetime", default=0.1,
                      help="How long tuning to given channel takes")
    parser.add_option("-s", "--summary", dest="summary", default=False,
                      help="Whether to print simulations parameter summary at end")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")
    parser.add_option("-f", "--file", dest="file",
                      help="Write output to file", metavar="FILE")
    
    # turn command line parameters into local variables
    (options, args) = parser.parse_args()
    model = options.model
    models = ['sync', 'async']
    if model not in models:
        print "Channel model %s no supported." % model
        sys.exit()
    
    num_overlap_channels = int(options.overlap_channels)
    num_channels = int(options.channels)
    theta = options.theta
    # Reset number of overlapping to number of total channels in sync mode
    if num_overlap_channels != num_channels and model == 'sync':
        num_overlap_channels = num_channels

    num_nodes = int(options.nodes)
    num_iterations = int(options.iterations)
    algorithm = options.algorithm
    verbose = options.verbose
    
    # Initialize seed, this helps reproducing the results
    np.random.seed(RANDOM_SEED)

    # Prepare statistics collection
    TTR = MinMaxMonitor()
    failed_counter = 0
    
    for run in range(num_iterations):
        # Create simulation environment
        nodes = createEnvironment(model, num_channels, num_overlap_channels, theta, num_nodes, algorithm, verbose)
        
        # Start rendezvous
        connected = False
        slot = 1
        while not connected:
            # For each node, get selected channel in this round
            current_channels = []
            for node in nodes:
                current_channels.append(node.getNextChannel(slot))

            # Check if all nodes have selected the same channel
            if isEqual(current_channels):
                #print "Rendezvous after %d slots." % slot
                TTR.tally(slot)
                connected = True
            slot += 1
            
            # Sanity check, after MAX_SLOTS, stop process
            if slot > MAX_SLOTS:
                connected = True
                failed_counter += 1
                

    #print "Stats after %d runs:" % (TTR.len())
    if failed_counter: print "Failed rendezvous tries: %d" % (failed_counter)
    print "%d\t%d\t%.2f\t%.2f\t%.2f\t%.2f" % (num_channels, num_overlap_channels, TTR.min(), TTR.mean(), TTR.max(), TTR.std())


if __name__ == "__main__":
    main()
