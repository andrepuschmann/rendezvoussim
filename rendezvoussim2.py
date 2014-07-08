#!/usr/bin/env python
"""
Simulation of a various rendezvous algorithms
"""
import sys
import numpy as np
from environment import Environment
from helper import MinMaxMonitor,isEqual,string_splitter,areNeighborChannels
from optparse import OptionParser

RANDOM_SEED = 42
MAX_SLOTS = 39999

def main():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("-a", "--algorithm", dest="algorithm", default=["random"],
                      help="Which rendezvous algorithm to simulate",
                      type='string', action='callback', callback=string_splitter)
    parser.add_option("-c", "--channels", dest="channels", default=5,
                      help="How many channels are available (the M parameter)")
    parser.add_option("-m", "--model", dest="model", default="symmetric",
                      help="Which channel model to use (symmetric or asymmetric)")
    parser.add_option("-g", "--overlappingchannels", dest="overlap_channels", type="int", default="5",
                      help="How many channels are overlapping between nodes (only for asymmetric model)")
    parser.add_option("-b", "--blockwidth", dest="block_width", type="int", default="1",
                      help="The width (in channels) of a block")
    parser.add_option("-t", "--theta-parameter", dest="theta", type="float", default="1.0",
                      help="The theta parameter defined in Liu's paper. It is multiplied with M to determine the actual number of channels per node")
    parser.add_option("-n", "--nodes", dest="nodes", default=2,
                      help="How many nodes are used")
    parser.add_option("-i", "--iterations", dest="iterations", default=1,
                      help="How often to repeat the simulation")
    parser.add_option("-r", "--randomreplace", dest="randomreplace", default=False, action="store_true",
                      help="Whether to replace unavailable channels with random ones")
    parser.add_option("-o", "--acdp", dest="acdp", type="float", default="0.0",
                      help="Probability that a beacon received in an adjacent channel can be detected")
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
    models = ['symmetric', 'asymmetric']
    if model not in models:
        print "Channel model %s not supported." % model
        sys.exit()
    
    num_overlap_channels = int(options.overlap_channels)
    num_channels = int(options.channels)
    theta = options.theta
    block_width = options.block_width
    acdp = options.acdp
    # Reset number of overlapping to number of total channels in sync mode
    if num_overlap_channels != num_channels and model == 'symmetric':
        num_overlap_channels = num_channels
    if num_channels < num_overlap_channels: num_overlap_channels = num_channels     

    num_nodes = int(options.nodes)
    num_iterations = int(options.iterations)
    algorithms = options.algorithm
    has_random_replace = options.randomreplace
    verbose = options.verbose

    # Initialize seed, this helps reproducing the results
    np.random.seed(RANDOM_SEED)

    # Prepare statistics collection in dictionaries
    ttr = {}
    for alg in algorithms:
        ttr[alg] = MinMaxMonitor()
    
    # Create simulation environment
    env = Environment(model, num_channels, num_overlap_channels, num_nodes, theta, block_width, verbose)
    
    for run in range(num_iterations):
        # reinitialize in each iteration (causes creation of new channels and nodes)
        env.initialize()
        
        nodes = env.getNodes()

        # Start rendezvous asynchronously, select node and number of iterations randomly
        async_slots = np.random.randint(1, num_channels * num_channels)
        #print "async_slots: %d" % async_slots
        #async_node = np.random.randint(0, num_nodes)
        async_node = 1 # Always let Node 1 start first to make sure this is the Master in centralized mode
        
        # Draw a random number that decides whether beacons on a neighbor channel can be detected
        neighbordetect_random = np.random.random_sample()
        
        # Evaluate each algorithm using the same environment
        for alg in algorithms:
            # Initialize nodes with actual algorithm
            env.initializeNodes(alg, has_random_replace)

            # asynchronous start
            for k in range(async_slots):
                nodes[async_node].getNextChannel()
            
            connected = False
            slot = 1
            while not connected:
                # For each node, get selected channel in this round
                current_channels = []
                for node in nodes:
                    current_channels.append(node.getNextChannel(slot))

                # Check if all nodes have selected the same channel
                if isEqual(current_channels):
                    #print "Rendezvous after %d slots in Channel %d." % (slot, current_channels[0].getId())
                    ttr[alg].tally(slot)
                    connected = True
                slot += 1
                
                # Check if two nodes have selected direct neighbors
                if areNeighborChannels(current_channels):
                    # make sure we detect such a situation only with a certain probability
                    if neighbordetect_random <= acdp:
                        # check, assume rendezvous has happened on two adjacent channels
                        # but for fairness add two more slots that are 
                        # needed to beacon on upper and lower neighbor (worst case)
                        slot += 2
                        ttr[alg].tally(slot)
                        connected = True
                else:
                    # FIXME: take probability of false alarm into account here
                    pass
                
                # Sanity check, after MAX_SLOTS, stop process
                if slot > MAX_SLOTS:
                    connected = True
    
    for alg in algorithms:
        num_ok = ttr[alg].len()
        num_failed = num_iterations - ttr[alg].len()
        if ttr[alg].len():
            # alg  num_channels   num_overlap_channels   num_iterations   num_ok   num_ok   ttr_min   ttr_mean   ttr_max   ttr_std   block_width   acdp   theta
            print "%s\t%d\t%d\t%d\t%d\t%d\t%.2f\t%.2f\t%.2f\t%.2f\t%d\t%.2f\t%.2f" % \
                        (alg, num_channels, num_overlap_channels, num_iterations, num_ok, num_failed, 
                        ttr[alg].min(), ttr[alg].mean(), ttr[alg].max(), ttr[alg].std(),
                        block_width, acdp, theta)
        else:
            print "No statistics collected."

    
    env.writeChannelMapsToFile()
    

if __name__ == "__main__":
    main()
