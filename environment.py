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
        
    def getMaxNumChannels(self):
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
        
    def getChannelIdsAsList(self):
        lst = []
        for chan in self.channels:
            lst.append(chan.getId())
        return lst
        
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
                self.algorithm = LowestIdFirstExhaustiveSearch(self.id, self.channelset, self.verbose)
            elif algorithm == "rex":
                self.algorithm = RandomizedExhaustiveSearch(self.id, self.channelset, self.verbose)
            elif algorithm == "lidfex":
                self.algorithm = LowestIdFirstExhaustiveSearch(self.id, self.channelset, self.verbose)    
            elif algorithm == "hidfex":
                self.algorithm = HighestIdFirstExhaustiveSearch(self.id, self.channelset, self.verbose)    
            elif algorithm == "lgfex":
                self.algorithm = LargestGapFirstExhaustiveSearch(self.id, self.channelset, self.verbose)
            elif algorithm == "sgfex":
                self.algorithm = SmallestGapFirstExhaustiveSearch(self.id, self.channelset, self.verbose)
            elif algorithm == "eofex":
                self.algorithm = EvenOddFirstExhaustiveSearch(self.id, self.channelset, self.verbose)
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
    def __init__(self, model, max_num_channels, num_overlap_channels, num_nodes, theta, block_width, verbose):
        self.name = "Environment"
        self.model = model
        self.max_num_channels = max_num_channels
        self.num_overlap_channels = num_overlap_channels
        self.num_nodes = num_nodes
        self.theta = theta
        self.block_width = block_width
        self.verbose = verbose
        self.channel_maps = [] # store for all channel maps that have been created in this env


    def initialize(self):
        # start environment creation
        self.nodes = self.createNodes(self.num_nodes, self.verbose)
        channels = self.createChannels(self.max_num_channels)

        if self.model == "symmetric":
            self.selectCommonChannels(channels, self.nodes, self.max_num_channels)
        elif self.model == "asymmetric":
            self.selectCommonChannels(channels, self.nodes, self.num_overlap_channels, self.block_width)
            self.selectIndividualChannels(channels, self.nodes, self.max_num_channels, self.num_overlap_channels, self.theta, self.block_width)

        # sort channel indices by ID
        for node in self.nodes:
            node.channelset.sortById()
            node.channelset.printChannels()
            
        # sanity check, there should be at least one overlapping channel
        self.checkForOverlappingChannel(self.nodes)
        
        # store channel map
        self.channel_maps.append(self.getOverlappingChannelsAsBitArray())
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
        

    def selectCommonChannels(self, channels, nodes, num, width):
        # Select G commonly available channels, try to satisfy block width
        num_blocks = int(np.ceil(num / float(width)))
        #print "num: %d" % num
        #print "width: %d" % width
        #print "num_blocks: %d" % num_blocks
        
        chan_ids = []
        for i in range(num_blocks):
            block = self.selectBlockOfChannels(channels, width)
            for id in block:
                chan_ids.append(id)

        # make sure not to have too many channels
        if len(chan_ids) > num:
            # sort first, then trim 
            chan_ids = sorted(chan_ids)
            num_trim = len(chan_ids) - num
            chan_ids = chan_ids[:-num_trim]

        # add channels to each node
        for id in chan_ids:
            chan = self.getChannelWithId(channels, id)
            if chan:
                for node in nodes:
                    node.appendChannels(chan)
                self.removeChannelWithId(channels, id)


    # Selects block of neighboring channels with specified width
    def selectBlockOfChannels(self, channels, width):
        chan_ids = []
        c = np.random.choice(channels)
        #print "c: %d" % c.getId()
        chan_ids.append(c.getId())

        # select upper and lower neighbor(s)
        lower_counter = 1
        upper_counter = 1
        for i in range(1, width):
            if i % 2 == 0:
                # if even, we remove the lower neighbor
                lower_neighbor = c.getId() - lower_counter
                #print "remove lower_neighbor: %d" % lower_neighbor
                chan_ids.append(lower_neighbor)
                lower_counter +=1
            else:
                # if odd, we remove the upper neighbor
                upper_neighbor = c.getId() + upper_counter
                #print "remove upper_neighbor: %d" % upper_neighbor
                chan_ids.append(upper_neighbor)
                upper_counter += 1

        # the upper selection process may select ids that are not sane, like -1, remove them
        chan_ids = [x for x in chan_ids if x >= 0]
        return chan_ids


    def selectIndividualChannels(self, channels, nodes, num_channels, num_overlap_channels, theta, width):
        # Distribute remaining channels over nodes
        num_missing = int(np.ceil((num_channels * theta) - num_overlap_channels))
        num_blocks = num_missing / width
        
        for node in nodes:
            for n in range(num_blocks):
                if channels:
                    block = self.selectBlockOfChannels(channels, width)
                    #print block
                    for id in block:
                        chan = self.getChannelWithId(channels, id)
                        if chan:
                            self.trace(0, "Channel %d is individual channel for node %d" % (chan.getId(), node.getId()))
                            node.appendChannels(chan)
                            channels.remove(chan)
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

    def writeChannelMapsToFile(self, filename='channelmap.dat'):
        # Write the array to disk
        with file(filename, 'w') as outfile:
            outfile.write('# In line in this file corresponds to the state of a channel, please see environment.py for details.\n')
            for data_slice in self.channel_maps:
                outfile.write('# Next iteration\n')
                np.savetxt(outfile, data_slice, fmt='%-.2f')

    def trace(self, slot=0, message=''):
        if self.verbose: print "%d: %s:\t%s" % (slot, self.name, message)
