from algorithms import *
from random import choice
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
    def __init__(self, id, algorithm=None, channels=None, verbose=True):
        self.id = id
        self.name = "Node " + str(id)
        self.algorithm_name = algorithm
        self.channels = channels
        self.verbose = verbose
        
    def initialize(self):
        self.trace(0, "Try to initialize node")
        self.no_channels = len(self.channels)
        if self.no_channels:
            if "random" in self.algorithm_name:
                self.algorithm = RandomRendezvous(self.no_channels, self.verbose)
            elif "sequence" in self.algorithm_name:
                self.algorithm = SequenceRendezvous(self.no_channels, False)
                #self.algorithm = SequenceRendezvous(self.no_channels, True)
                self.algorithm.printSequence()
            elif "modularclock" in self.algorithm_name:
                self.algorithm = ModularClockRendezvous(self.no_channels, self.verbose)
            elif "jumpstay" in self.algorithm_name:
                self.algorithm = JSHoppingRendezvous(self.no_channels, self.verbose)
            else:
                print "Rendezvous algorithm %s is not supported." % (self.algorithm_name)
                sys.exit()   
        else:
            self.trace(0, "No channels given, initialize later ..")

        
    def setChannels(self, channels):
        self.channels = channels
        self.no_channels = len(self.channels)

    def appendChannels(self, channels):
        self.channels.append(channels)
    
    def printChannels(self):
        self.trace(0, "My channels: %d" % len(self.channels))
        for i in self.channels:
            self.trace(message="  %s, id: %d" % (i.getName(), id(i)))


    def getNextChannel(self, slot):
        self.trace(slot, "Determine next channel ...")
        r = self.algorithm.getNextIndex()
        self.trace(slot, "Next channel has index %d, id of channel is %d" % (r, self.channels[r].getId()))
        # check validity
        if r > (self.no_channels - 1):
            print "Error, too large channel index"
            sys.exit()
        return self.channels[r].getId()
        
    def trace(self, slot=0, message=''):
        if self.verbose: print "%d: %s:\t%s" % (slot, self.name, message)




class Environment():
    def __init__(self, model, num_channels, num_overlap_channels, num_nodes, algorithm, verbose):
        self.name = "Environment"
        self.verbose = verbose
        
        self.nodes = self.createNodes(num_nodes, algorithm, verbose)
        channels = self.createChannels(num_channels)
        
        theta = 0.5
        
        if model == "sync":
            self.selectCommonChannels(channels, self.nodes, num_channels)
        elif model == "async":
            self.selectCommonChannels(channels, self.nodes, num_overlap_channels)
            self.selectIndividualChannels(channels, self.nodes, num_channels, num_overlap_channels, theta)
        
        # sort channel indices (FIXME: this causes varying results)
        #for node in self.nodes:
        #    node.channels = sorted(node.channels, key=lambda chan: chan.getId())   # sort by ID
        
        # initialize nodes
        for node in self.nodes:
            node.initialize()
        
        for node in self.nodes:
            node.printChannels()


    def createNodes(self, num, algorithm, verbose):
        # Create nodes and initialize them with empty channel list
        nodes = []
        for n in range(num):
            nodes.append(Node(n + 1, algorithm, [], verbose))
        return nodes


    def initializeNodes(self):
        for node in self.nodes:
            node.initialize()


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
            c = choice(channels)
            self.trace(0, "Channel %d is %d. common channel" % (c.getId(), i + 1))
            # append to each nodes' channel list
            for node in nodes:
                node.appendChannels(c)
            channels.remove(c)


    def selectIndividualChannels(self, channels, nodes, num_channels, num_overlap_channels, theta):
        # Distribute remaining channels over nodes
        no_missing = int(np.ceil((num_channels * theta) - num_overlap_channels))
        for node in nodes:
            for n in range(no_missing):
                if channels:
                    c = choice(channels)
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

