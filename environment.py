from algorithms import *
import numpy as np
import sys

class Channel():
    def __init__(self, id):
        self.id = id
        self.name = "Channel " + str(id)
                
    def getId(self):
        return self.id

    def getName(self):
        return self.name


class Node():
    def __init__(self, id, verbose=True):
        self.id = id
        self.name = "Node " + str(id)
        self.channels = []
        self.verbose = verbose

    def configure(self, max_num_channels=-1):
        self.max_num_channels = max_num_channels

    def initialize(self, algorithm=None, has_random_replace=False):
        self.trace(0, "Try to initialize node")
        self.num_channels = len(self.channels) # The actual number of accessible channels
        self.has_random_replace = has_random_replace
        
        algorithm = algorithm.strip()
        
        # If random replace is turned on, we pass max_num_channels to the algorithm 
        # instead of the actual number of channels of a node
        if self.has_random_replace == True:
            num_channels_algorithm = self.max_num_channels
        else:
            num_channels_algorithm = self.num_channels
                
        if self.num_channels > 0 and algorithm != None:
            if algorithm == "random":
                self.algorithm = RandomRendezvous(num_channels_algorithm, self.verbose)
            elif algorithm == "seq":
                self.algorithm = SequenceRendezvous(num_channels_algorithm, False)
                #self.algorithm = SequenceRendezvous(num_channels_algorithm, True)
                self.algorithm.printSequence()
            elif algorithm == "mc":
                self.algorithm = ModularClockRendezvous(num_channels_algorithm, self.verbose)
            elif algorithm == "js":
                self.algorithm = JSHoppingRendezvous(num_channels_algorithm, self.verbose)
            elif algorithm == "crseq":
                self.algorithm = CRSeqRendezvous(num_channels_algorithm, self.verbose)
            else:
                print "Rendezvous algorithm %s is not supported." % (algorithm)
                sys.exit()   
        else:
            self.trace(0, "No channels or algorithm given, initialize later ..")


    def appendChannels(self, channels):
        self.channels.append(channels)
    
    def printChannels(self):
        self.trace(0, "My channels: %d" % len(self.channels))
        for i in self.channels:
            self.trace(message="  %s, id: %d" % (i.getName(), id(i)))

    def getNextChannel(self, slot=0):
        self.trace(slot, "Determine next channel ...")
        r = self.algorithm.getNextIndex()
        if self.has_random_replace:
            if r > (self.num_channels - 1):
                r = np.random.randint(0, self.num_channels)
        
        # check validity
        if r > (self.num_channels - 1):
            print "Error, too large channel index"
            sys.exit()
        self.trace(slot, "Next channel has index %d, id of channel is %d" % (r, self.channels[r].getId()))
        return self.channels[r].getId()
        
    def trace(self, slot=0, message=''):
        if self.verbose: print "%d: %s:\t%s" % (slot, self.name, message)




class Environment():
    def __init__(self, model, max_num_channels, num_overlap_channels, num_nodes, theta, verbose):
        self.name = "Environment"
        self.verbose = verbose
        self.max_num_channels = max_num_channels

        # start environment creation
        self.nodes = self.createNodes(num_nodes, verbose)
        channels = self.createChannels(max_num_channels)

        if model == "sync":
            self.selectCommonChannels(channels, self.nodes, max_num_channels)
        elif model == "async":
            self.selectCommonChannels(channels, self.nodes, num_overlap_channels)
            self.selectIndividualChannels(channels, self.nodes, max_num_channels, num_overlap_channels, theta)

        # sort channel indices by ID
        for node in self.nodes:
            node.channels = sorted(node.channels, key=lambda chan: chan.getId())

        for node in self.nodes:
            node.printChannels()


    def createNodes(self, num_nodes, verbose):
        # Create nodes and initialize them with empty channel list
        nodes = []
        for n in range(num_nodes):
            nodes.append(Node(n + 1, verbose))
        return nodes


    def initializeNodes(self, algorithm=None, has_random_replace=False):
        for node in self.nodes:
            node.configure(self.max_num_channels)
            node.initialize(algorithm, has_random_replace)


    def createChannels(self, num):
        # Create pool of available channels (numbered from zero to M-1)
        pool = []
        for i in range(num):
            pool.append(Channel(i))
        
        self.trace(0, "Pool has %d channels" % len(pool))
        return pool


    def selectCommonChannels(self, channels, nodes, num):
        # Select G commonly available channels
        for i in range(num):
            c = np.random.choice(channels)
            self.trace(0, "Channel %d is %d. common channel" % (c.getId(), i + 1))
            # append to each nodes' channel list
            for node in nodes:
                node.appendChannels(c)
            channels.remove(c)


    def selectIndividualChannels(self, channels, nodes, num_channels, num_overlap_channels, theta):
        # Distribute remaining channels over nodes
        num_missing = int(np.ceil((num_channels * theta) - num_overlap_channels))
        for node in nodes:
            for n in range(num_missing):
                if channels:
                    c = np.random.choice(channels)
                    self.trace(0, "Channel %d is individual channel for node %d" % (c.getId(), n))
                    node.appendChannels(c)
                    channels.remove(c)
                else:
                    print "Warning: M not large enough to satisfy N=M*theta!"
                    pass


    def getNodes(self):
        return self.nodes


    def getName(self):
        return self.name


    def trace(self, slot=0, message=''):
        if self.verbose: print "%d: %s:\t%s" % (slot, self.name, message)

