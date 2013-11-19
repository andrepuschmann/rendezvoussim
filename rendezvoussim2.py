#!/usr/bin/env python
"""
Simulation of a various rendezvous algorithms
"""
import sys
import matplotlib.pyplot as plt
import numpy as np
#import pylab as P

from environment import Channel,Node,Environment

from helper import *
from optparse import OptionParser

RANDOM_SEED = 42
MAX_SLOTS = 39999

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
    # Reset number of overlapping to number of total channels in sync mode
    if num_overlap_channels != num_channels and model == 'sync':
        num_overlap_channels = num_channels
    if num_channels < num_overlap_channels: num_overlap_channels = num_channels     

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
        env = Environment(model, num_channels, num_overlap_channels, num_nodes, algorithm, verbose)
        nodes = env.getNodes()
        
        #nodes = createEnvironment(model, num_channels, num_overlap_channels, num_nodes, algorithm, verbose)
        
        # Start rendezvous
        # async start, let fist node run for a while before second
        for i in range(np.random.randint(0, num_channels)):
            nodes[0].getNextChannel(i)
        
        connected = False
        slot = 1
        while not connected:
            # For each node, get selected channel in this round
            current_channels = []
            for node in nodes:
                current_channels.append(node.getNextChannel(slot))

            # Check if all nodes have selected the same channel
            if isEqual(current_channels):
                #print "Rendezvous after %d slots in Channel %d." % (slot, current_channels[0])
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
