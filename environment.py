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


class ChannelSet():
    def __init__(self, verbose=True):
        self.name = "ChannelSet"
        self.channels = []
        self.max_num_channels = -1
        self.verbose = verbose
        
    def add_channel(self, channel):
        if len(self.channels) != self.max_num_channels:
            self.channels.append(channel)
        else:
            self.trace(0, "Failed to add channel with id %d, maximum number reached." % channel.getId())

    def setMaxNumChannels(self, num):
        self.max_num_channels = num
    
    def getNumChannels(self):
        return len(self.channels)
        
    def get_max_num_channels(self):
        return self.max_num_channels
        
    def hasChannelWithId(self, id):
        for chan in self.channels:
            if chan.getId() == id:
                return True
        return False
        
    def hasChannel(self, channel):
        if channel in self.channels:
            return True
        return False
    
    def getChannelsAsList(self):
        return self.channels
        
    def getChannelById(self, id):
        for chan in self.channels:
            if chan.getId() is id:
                return chan
                
    def sortById(self):
        self.channels = sorted(self.channels, key=lambda chan: chan.getId())
        
    def getChannelByIndex(self, pos):
        return self.channels[pos]
        
    def printChannels(self):
        self.trace(0, "My channels: %d" % self.getNumChannels())
        for i in self.channels:
            self.trace(message="  %s, id: %d" % (i.getName(), id(i)))        

    def trace(self, slot=0, message=''):
        if self.verbose: print "%d: %s:\t%s" % (slot, self.name, message)
        
        

class Node():
    def __init__(self, id, verbose=True):
        self.id = id
        self.name = "Node " + str(id)
        self.channelset = ChannelSet(verbose)
        self.verbose = verbose
    
    def getId(self):
        return self.id
    
    def configure(self, max_num_channels=-1):
        self.channelset.setMaxNumChannels(max_num_channels)

    def initialize(self, algorithm=None, has_random_replace=False):
        self.trace(0, "Try to initialize node")
        self.has_random_replace = has_random_replace
        
        algorithm = algorithm.strip()               
        if algorithm != None:
            if algorithm == "random":
                self.algorithm = RandomRendezvous(self.channelset, self.verbose)
            elif algorithm == "seq":
                self.algorithm = SequenceRendezvous(self.channelset, False)
                #self.algorithm = SequenceRendezvous(num_channels_algorithm, True)
                self.algorithm.printSequence()
            elif algorithm == "mc":
                self.algorithm = ModularClockRendezvous(self.channelset, self.verbose)
            elif algorithm == "js":
                self.algorithm = JSHoppingRendezvous(self.channelset, self.verbose)
            elif algorithm == "crseq":
                self.algorithm = CRSeqRendezvous(self.channelset, self.verbose)
            elif algorithm == "ex":
                self.algorithm = ExhaustiveSearch(self.id, self.channelset, self.verbose)
            elif algorithm == "rex":
                self.algorithm = RandomizedExhaustiveSearch(self.id, self.channelset, self.verbose)
            elif algorithm == "hgrex":
                self.algorithm = HeuristicallyGuidedRandomizedExhaustiveSearch(self.id, self.channelset, self.verbose)
            else:
                print "Rendezvous algorithm %s is not supported." % (algorithm)
                sys.exit()   
        else:
            self.trace(0, "No channels or algorithm given, initialize later ..")


    def appendChannels(self, channels):
        self.channelset.add_channel(channels)


    def getChannelSet(self):
        return self.channelset


    def getNextChannel(self, slot=0):
        self.trace(slot, "Determine next channel ...")
        r = self.algorithm.getNextChannel()
        # check validity
        if self.channelset.hasChannel(r) == False:
            print "Node %s doesn't have channel with id: %d" % (self.name, r.getId())
            sys.exit()
        self.trace(slot, "Next channel has id: %d" % r.getId())
        return r
        
    def trace(self, slot=0, message=''):
        if self.verbose: print "%d: %s:\t%s" % (slot, self.name, message)



class Environment():
    def __init__(self, model, max_num_channels, num_overlap_channels, num_nodes, theta, verbose):
        self.name = "Environment"
        self.verbose = verbose
        self.max_num_channels = max_num_channels
        self.num_overlap_channels = num_overlap_channels
        
        self.num_pu_node1 = 2
        self.num_pu_node2 = 2
        self.num_pu_both = 4
        self.pu_width = 5
        
        self.scenario = "random"
        #self.scenario = "deterministic"

        # start environment creation
        self.nodes = self.createNodes(num_nodes, verbose)
        channels = self.createChannels(max_num_channels)

        if model == "symmetric":
            self.selectCommonChannels(channels, self.nodes, max_num_channels)
        elif model == "asymmetric":
            if self.scenario == "random":
                self.selectCommonChannels(channels, self.nodes, num_overlap_channels)
                self.selectIndividualChannels(channels, self.nodes, max_num_channels, num_overlap_channels, theta)
            else:
                self.placePu(channels, self.nodes, self.num_pu_node1, self.num_pu_node2, self.num_pu_both, self.pu_width)

        # sort channel indices by ID
        for node in self.nodes:
            node.channelset.sortById()
            node.channelset.printChannels()
            
        # sanity check, there should be at least one overlapping channel
        self.checkForOverlappingChannel(self.nodes)

        #sys.exit()


    def createNodes(self, num_nodes, verbose):
        # Create nodes and initialize them with empty channel list
        nodes = []
        for n in range(num_nodes):
            nodes.append(Node(n, verbose))
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

    def getChannelWithId(self, channels, id):
        for chan in channels:
            #print "id is: %d" % chan.getId()
            if chan.getId() is id:
                return chan

    def removeChannelWithId(self, channels, id):
        for chan in channels:
            if chan.getId() == id:
                channels.remove(chan)


    # This function creates PUs in the sourrounding of a node making the
    # channels unavailable for that node, but available for the other one
    def createPuAtNodePossition(self, channels, num, width, id):
        # determine other node where channels are available
        id_available = []
        for node in self.nodes:
            if node.getId() not in id:
                id_available.append(node.getId())
                
        #print id_available

        for i in range(num):
            # Select center channel randomly
            chan_ids = []
            c = np.random.choice(channels)
            chan_ids.append(c.getId())

            # select upper and lower neighbor(s)
            num_upper_lower = int((width - 1) / 2)
            #print "num_upper_lower: %d" % num_upper_lower
            for x in range(1, num_upper_lower + 1):
                #print "x: %d" % x
                lower_neighbor = c.getId() - x
                upper_neighbor = c.getId() + x
                chan_ids.append(lower_neighbor)
                chan_ids.append(upper_neighbor)
                #print "remove lower_neighbor: %d" % lower_neighbor
                #print "remove upper_neighbor: %d" % upper_neighbor

            # Try to remove all channels 
            for id in chan_ids:
                if len(channels) > self.num_overlap_channels:
                    #print "id: %d" % id
                    chan = self.getChannelWithId(channels, id)
                    if chan:
                        for node in id_available:
                            self.nodes[node].appendChannels(chan)
                        self.trace(0, "Channel %d is PU channel %d" % (chan.getId(), i + 1))
                        self.removeChannelWithId(channels, id)
                else:
                    print "Stop PU creation due to lack of channels"

            #sys.exit()


    def placePu(self, channels, nodes, num_pu_node1, num_pu_node2, num_pu_both, width):
        #print "width: %d" % width
        #print "num_pu_node1: %d" % num_pu_node1
        #print "num_pu_node2: %d" % num_pu_node2
        #print "num_pu_both: %d" % num_pu_both
        
        
        #print "Create PU around node1"
        self.createPuAtNodePossition(channels, num_pu_node1, width, [0])
        
        #print "Create PU around node2"
        self.createPuAtNodePossition(channels, num_pu_node2, width, [1])
        
        #print "Create PU around both nodes"
        self.createPuAtNodePossition(channels, num_pu_both, width, [0,1])
        
        remaining_channels = len(channels)
        #print "remaining_channels: %d" % remaining_channels
        if remaining_channels < 1:
            print "Error, not enough channels"
            sys.exit()
        
        # distribute remaining channels over nodes
        for chan in channels:
            #print "Id: %d" % chan.getId()
            for node in nodes:
                node.appendChannels(chan)
        channels = []
        

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


    def calculateChannelStatistics(self):
        result = []
        for node in self.nodes:
            channels = node.channelset.getChannelsAsList()
            chan_list = [chan.getId() for chan in channels]
            binarymap = [0 for x in range(self.max_num_channels)] # initialize map to zero
            # iterate over channel list and mark available channels
            for c in chan_list:
                binarymap[c] = 1
            result.append(binarymap)

        # Calculate intersection of all channel sets (works only for two users)
        if len(result) == 2:
            intersect = []
            for (x,y) in zip(result[0],result[1]):
                if ((x is 1) and (y is 1)):
                    intersect.append(1)
                elif (x is 1):
                    intersect.append(0.66)
                elif (y is 1):
                    intersect.append(0.33)
                else:
                    intersect.append(0)
            result.append(intersect)

        else:
            print "Intersection only implemented for two users."
            sys.exit()

        return result
    
    def checkForOverlappingChannel(self, nodes):
        overlappingChannelFound = False
        assert len(nodes) == 2
        # Check if both nodes have at least one channel in common
        channelSet = nodes[0].getChannelSet()
        for i in range(channelSet.getNumChannels()):
            if nodes[1].getChannelSet().hasChannel(channelSet.getChannelByIndex(i)) == True:
                overlappingChannelFound = True

        if not overlappingChannelFound:
            print "No overlapping channel found, please check environment configuration"
            sys.exit()


    def getOverlappingChannelsAsBitArray(self):
        return self.calculateChannelStatistics()[2]


    def getNodes(self):
        return self.nodes


    def getName(self):
        return self.name


    def trace(self, slot=0, message=''):
        if self.verbose: print "%d: %s:\t%s" % (slot, self.name, message)

