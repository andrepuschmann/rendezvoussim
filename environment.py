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
        #self.printChannels()
        
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
        self.model = model
        self.M = num_channels
        self.G = num_overlap_channels
        self.K = num_nodes
        self.algorithm = algorithm
        self.verbose = verbose
        
        self.createNodes()
        self.createChannelPool()
        
        if model == "sync":
            self.selectCommonChannels(self.nodes)
        elif model == "async":
            self.selectCommonChannels(self.nodes)
            self.selectIndividualChannels(self.nodes)
        else:
            sys.exit()

        # sort channel indexes
        #for node in self.nodes:
        #    node.channels.sort(key=lambda x: x.getId(), reverse=False)


        for node in self.nodes:
            node.printChannels()
            
        #sys.exit()

        self.initializeNodes()
        
    def createNodes(self):
        # Create nodes and initialize them with empty channel list
        self.nodes = []
        for n in range(self.K):
            self.nodes.append(Node(n + 1, self.algorithm, [], self.verbose))
            
    def initializeNodes(self):
        for node in self.nodes:
            node.initialize()

    def createChannelPool(self):
        # Create pool of available channels (numbered from zero to M-1)
        self.channel_pool = []
        for i in range(self.M):
            self.channel_pool.append(Channel(i))
        
        self.trace(0, "Pool has %d channels" % len(self.channel_pool))

    def selectCommonChannels(self, nodes):
        # Select G commonly available channels
        for i in range(self.G):
            c = choice(self.channel_pool)
            self.trace(0, "Channel %d is %d. common channel" % (c.getId(), i + 1))
            # append to each nodes' channel list
            for node in nodes:
                node.appendChannels(c)
            self.channel_pool.remove(c)

    def selectIndividualChannels(self, nodes):
        # Distribute remaining channels equally over nodes
        while self.channel_pool:
            for n in range(len(nodes)):
                try:
                    c = choice(self.channel_pool)
                    self.trace(0, "Channel %d is individual channel for node %d" % (c.getId(), n))
                    nodes[n].appendChannels(c)
                    self.channel_pool.remove(c)
                except IndexError:
                    pass # Nodes have unequal number of channels

    def getNodes(self):
        return self.nodes

    def getName(self):
        return self.name

    def trace(self, slot=0, message=''):
        if self.verbose: print "%d: %s:\t%s" % (slot, self.name, message)

