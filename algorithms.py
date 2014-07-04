import numpy as np
from time import sleep
import sys
from collections import defaultdict

def getNextPrime(M=1, greaterOnly=False):
    def is_prime(n):
        """ check if n is prime"""
        i = 2
        if n <=1:
            return False
        Sqrt_Of_n = n**0.5
        while i <= Sqrt_Of_n:
            if n % i == 0:
                return False
            i += 1
        else:
            return True
            
    i = M
    if i < 2: return 2
    for i in range(i,2*M):
        if is_prime(i):
            if greaterOnly:
                if M != i:
                    break
            else:
                break
    return i



class Rendezvous():
    def __init__(self, name, channelset, verbose=True):
        self.name = name
        self.channelset = channelset
        self.M = channelset.getMaxNumChannels()
        self.N = channelset.getNumChannels()
        self.verbose = verbose
 
    def getName(self):
        return self.name

    def trace(self, message=''):
        if self.verbose: print "   %s:\t%s" % (self.name, message)           


class RandomRendezvous(Rendezvous):
    def __init__(self, channelset, verbose):
        Rendezvous.__init__(self, "Random", channelset, verbose)
    
    """ override base class function, return random channel number between 0 and number of channels """
    def getNextChannel(self):
        #print "num channels: %d" % self.N
        r = np.random.randint(0, self.N) # draw random number between 0 and nr_of_channels
        #print "rand: %d" % r
        return (self.channelset.getChannelByIndex(r))



class ModularClockRendezvous(Rendezvous):
    def __init__(self, channelset, verbose):
        Rendezvous.__init__(self, "ModularClock", channelset, verbose)
        self.nr_of_channels = channelset.getNumChannels()
        self.p = getNextPrime(self.nr_of_channels)
        self.j_old = np.random.randint(0, self.nr_of_channels) # pick first channel randomly
        self.renew_rate()
        self.current_slot = 1
        self.trace("prime: %d" % self.p)
        self.trace("j_old: %d" % self.j_old)        

    def renew_rate(self):
        self.r = np.random.randint(0, self.p) # pick hopping "rate"
        self.trace("rate: %d" % self.r)

    def getNextChannel(self):
        # renew rate every 2*p slots
        self.trace("Currslot: %d" % self.current_slot)
        if self.current_slot > (2*self.p):
            self.renew_rate()
            self.current_slot = 1
        else:
            self.current_slot += 1
        
        # calculate new channel
        j_new = (self.j_old + self.r) % self.p
        self.trace("j_new: %d" % j_new)
        # wrap around if needed
        if j_new < self.nr_of_channels:
            c = j_new
        else:
            c = j_new % self.nr_of_channels
            self.trace("c: %d" % c)
        self.j_old = j_new # overwrite old value       
        return (self.channelset.getChannelByIndex(c))

class SequenceRendezvous(Rendezvous):
    def __init__(self, nr_of_channels, use_preset=False):
        Rendezvous.__init__(self, "Sequence", nr_of_channels)
        self.nr_of_channels = int(nr_of_channels)
        # add preset sequences (taken from DaSilva paper)
        self.preset_sequences = {3 : [0,0,1,2,1,1,0,2,2,2,0,1], 
                                 4 : [0,0,0,1,2,3,1,1,1,0,2,3,2,2,2,0,1,3,3,3,3,0,1,2],
                                 5 : [1,2,4,3,0,0,1,4,3,2,3,4,2,1,0,3,1,4,2,0,2,3,4,0,1,2,3,1,4,0] }
        
        # check whether to create own sequence or use one of the above
        create_sequence = True
        if use_preset == True:
            # check if preset is available for given nr of channels
            if self.nr_of_channels in self.preset_sequences:
                self.trace(0, "Using preset sequence.")
                self.sequence = self.preset_sequences[self.nr_of_channels]
                create_sequence = False
            else:
                self.trace(0, "No preset sequence for given number of channels found, creating one.")

        if create_sequence == True:
            self.sequence = self.createSequence()
            
        # Initialize starting index to random number
        self.index = np.random.randint(0, self.nr_of_channels)
        self.trace("Start index: %d" % self.index)

    
    def createSequence(self):
        # create random permutation first
        permutation = []
        while len(permutation) != int(self.nr_of_channels):
            # create random index
            r = np.random.randint(0, self.nr_of_channels) # draw random number between 0 and nr_of_channels
            # check if r is already part of the list
            if not r in permutation:
                permutation.append(r)
        
        # the actual sequence is now created by taking each element of the
        # permutation and appending the permutation itself
        sequence = []
        for i in range(int(self.nr_of_channels)):
            # add the i'th element of permutation
            sequence.append(permutation[i])
            # plus the entire permutation
            for p in permutation:
                sequence.append(p)
        
        # finally return sequence
        return sequence


class JSHoppingRendezvous(Rendezvous):
    def __init__(self, channelset, verbose):
        Rendezvous.__init__(self, "JSHopping", channelset, verbose)
        
        # initialize algorithm
        self.P = getNextPrime(self.N)
        self.r = np.random.randint(1, self.N + 1)
        self.i = np.random.randint(1, self.P + 1)
        self.t = 0 # current time slot
        #self.test()

    # Simple functional test using the parameter given in the paper
    def test(self):
        print "JSPattern test"
        N = 4
        r = 1
        i = 3
        P = getNextPrime(N)
        round = self.JSHopping(N, P, r, i)
        print round

    def update_r(self):
        self.r = ((self.r + 1) % (self.N + 1))
        if self.r == 0: self.r = 1
        self.trace("New r: %d" % self.r)

    def update_i(self):
        self.i = ((self.i + 1) % (self.N + 1))
        if self.i == 0: self.i = 1
        self.trace("New i: %d" % self.i)
    
    # Just call JumpStay here
    def getNextChannel(self):
        c = self.JumpStay()
        # in simulation, channels start with index 0, do remapping
        c -= 1
        #print "c: %d" % c
        return (self.channelset.getChannelByIndex(c))
        
    # Technically, this is the inner loop of the JS_2 algorithm
    def JumpStay(self):
        # Update r every 3*P time slots
        if (self.t % (3 * self.P)) == 0:
            self.trace("Update r in this round")
            self.update_r()
        # Update i every 3*M*P slots
        if (self.t % (3 * self.N * self.P)) == 0:
            self.trace("Update i in this round")
            self.update_i()
        
        # get channel for this specific slot
        c = self.JSHopping(self.N, self.P, self.r, self.i, self.t)
        self.trace("Slot: %d" % self.t)
        self.trace("CH Index: %d" % c)
        self.t += 1 # increment slot counter
        return c

    # Generate one round JS hopping sequence for the given paramaters
    def JSHopping(self, N, P, r, i, slot=-1):
        nextround = []
        for t in range(3*P):
            t = t % (3*P)   # each round takes 3P timeslots
            if t < (2*P):
                # jump pattern
                j = ((i + t*r -1) % P) + 1
            else:
                # stay pattern
                j = r
            if (j > N):
                l = j
                j = ((j - 1) % N) + 1 # remapping
                
            nextround.append(int(j))
        if len(nextround) != 3*P:
            print "ERROR!"

        # return specific slot if t is given, return the whole round otherwise
        self.trace(nextround)
        if slot >= 0:
            # wrap around 3*P cause slot can get bigger than that
            slot = (slot) % (3*P)
            return nextround[slot]
        return nextround


class ExtendedJSHoppingRendezvous(Rendezvous):
    def __init__(self, nr_of_channels):
        Rendezvous.__init__(self, "EJS", nr_of_channels)
        self.sequence = self.createSequence()
        #print self.printSequence()


class CRSeqRendezvous(Rendezvous):
    def __init__(self, channelset, verbose):
        Rendezvous.__init__(self, "CRSEQ", channelset, verbose)
        # initialize algorithm
        self.P = getNextPrime(self.N)
        self.t = 0 # current time slot
        self.trace("self.N: %d" % self.N)
        self.trace("self.P: %d" % self.P)
        #self.test2()

    # Simple functional test using the parameter given in the paper
    def test(self):
        print "CRSEQPattern test"
        N = 20
        print "N: %d" % N
        P = getNextPrime(N)
        print "P: %d" % P
        
        # Run CRSEQ for 3*M slots
        seq = []
        for i in range(3*P-1):
            c = self.CRSEQHopping(N, P, i)
            seq.append(c)
        print seq
        sys.exit()
        
    def test2(self):
        print "CRSEQ test"
        N = 20
        print "N: %d" % N
        P = getNextPrime(N)
        print "P: %d" % P        
        c = self.CRSEQHopping(N, P, 739674)
        print c
        sys.exit()
        
    
    def getNextChannel(self):
        c = self.CRSEQHopping(self.N, self.P, self.t)
        self.t += 1
        self.trace("Next channel index: %d" % c)
        #return c
        return (self.channelset.getChannelByIndex(c))

    def CRSEQHopping(self, N, P, slot):
        self.trace("-----")
        self.trace("N: %d" % N)
        self.trace("P: %d" % P)
        self.trace("Slot: %d" % slot)
        maxSeqLen = P * (3 * P - 1)
        self.trace("maxSeqLen: %d" % maxSeqLen)
        maxSubSeqLen = 3 * P - 1 # subsequence length
        self.trace("maxSubSeqLen: %d" % maxSubSeqLen)

        slot = slot % maxSeqLen
        self.trace("newslot: %d" % slot)
        
        subSeqSlot = slot % maxSubSeqLen
        self.trace("subSeqSlot: %d" % subSeqSlot)

        j = int(np.floor(slot / maxSubSeqLen)) # subsequence that we are in
        self.trace("j: %d" % j)
        
        # Calculate T_j (or T_n as called in the paper)
        Tj = ((j * (j + 1) / 2) + subSeqSlot) % P
        self.trace("Tj: %d" % Tj)
        
        if subSeqSlot < (2 * P - 1):
            return Tj % N
        else:
            return j % N



# Base class for all Exhaustive Search variants
class ExhaustiveSearch(Rendezvous):
    def __init__(self, name, node_id, channelset, verbose=True):
        Rendezvous.__init__(self, name, channelset, verbose)
        self.isMaster = False
        self.masterHoppingSequence = []
        self.slaveHoppingSequence = []
        self.currentMasterIndex = -1
        self.currentSlaveIndex = -1
        self.t = -1
        if node_id == 1:
            self.isMaster = True
            self.trace("I am the master")   
        else:
            self.trace("I am a slave")


    def getNextChannel(self):
        self.t = self.t + 1
        if self.isMaster:
            return self.getNextChannelMaster()
        else:
            return self.getNextChannelSlave()

            
    def getNextChannelMaster(self):
        # Choose new channel in each slot and iterate through available 
        # channels, starting with lowest index
        sequence_len = len(self.masterHoppingSequence)
        self.currentMasterIndex = (self.currentMasterIndex + 1) % sequence_len
        self.trace("masterChannel: %d" % self.currentMasterIndex)
        
        channelId = self.masterHoppingSequence[self.currentMasterIndex]
        return self.channelset.getChannelById(channelId)

        
    def getNextChannelSlave(self):
        # Stay in one channel for N slots to make sure the slave catches
        # up, choose next channel in every Nth slot
        # FIXME: We assume N to be the same for master and slave here
        # As the actual number of channels of the master is not know, we can
        # use N as an upper bound here to make sure, we really hit the master
        sequence_len = len(self.slaveHoppingSequence)
        if (self.t % self.N) == 0:
            self.currentSlaveIndex = (self.currentSlaveIndex + 1) % sequence_len
            self.trace("Update master channel, id is: %d" % self.slaveHoppingSequence[self.currentSlaveIndex])
        
        channelId = self.slaveHoppingSequence[self.currentSlaveIndex]
        return self.channelset.getChannelById(channelId)


    def getSortedListById(self, channelset, reverse=False):
        # iterate through channels, add indices to sorted list
        unsort_list = []
        for i in range(channelset.getNumChannels()):
            unsort_list.append(channelset.getChannelByIndex(i).getId())
        return sorted(unsort_list, reverse=reverse)


    def getSortedListByGapSize(self, channelset, reverse=False):
        # sort channels according to gap size
        channel_dict = defaultdict(list)
        last_id = -2
        current_gap_size = 1
        for i in range(channelset.getNumChannels()):
            #print "id at pos %d: %d" % (i, channelset.getChannelByIndex(i).getId())
            current_id = channelset.getChannelByIndex(i).getId()
            #print "current_id: %d" % current_id
            #print "last_id: %d" % last_id
            if current_id == (last_id + 1):
                #print "found consecutive channels"
                current_gap_size += 1
            elif last_id == -2:
                last_id = current_id
            else:
                #print "gap size of previous n channels was: %d" % current_gap_size
                last_gap = []
                #last_gap = [id for i in xrange(current_gap_size)
                for i in xrange(current_gap_size):
                    last_gap.append(last_id - i)
                # append sorted list to dictionary of channels
                channel_dict[current_gap_size].append(sorted(last_gap))
                current_gap_size = 1
            last_id = current_id
            #print "---"
        
        # Handle last channels
        if current_gap_size:
            #print "gap size at end: %d" % current_gap_size
            last_gap = []
            for i in xrange(current_gap_size):
                last_gap.append(last_id - i)
            channel_dict[current_gap_size].append(sorted(last_gap))
        
        # Write dict, sorted by keys, to list
        keylist = channel_dict.keys()
        keylist.sort(reverse=reverse)
        target = []
        for key in keylist:
            #print "key: %d" % key
            #print channel_dict[key]
            for idlist in channel_dict[key]:
                for id in idlist: 
                    target.append(channelset.getChannelById(id).getId())
        
        #print "-----------"
        #print channel_dict
        return target


    def getRandomList(self, channelset):
        lst = self.channelset.getChannelIdsAsList()       
        return np.random.permutation(lst).tolist()


# A randomized, but exhaustive version
class RandomizedExhaustiveSearch(ExhaustiveSearch):
    def __init__(self, node_id, channels, verbose):
        ExhaustiveSearch.__init__(self, "REX", node_id, channels, verbose)

        if self.isMaster:
            self.masterHoppingSequence = self.getRandomList(channels)
        else:
            self.slaveHoppingSequence = self.getRandomList(channels)


# Four heuristically guided variants
class LowestIdFirstExhaustiveSearch(ExhaustiveSearch):
    def __init__(self, node_id, channels, verbose):
        ExhaustiveSearch.__init__(self, "LIDFEX", node_id, channels, verbose)

        # Sort channels in accending order according to channel ID (normal EX algorithm)
        if self.isMaster:
            self.masterHoppingSequence = self.getSortedListById(channels, reverse=False)
            #print "i am master"
            #print self.masterHoppingSequence
        else:
            self.slaveHoppingSequence = self.getSortedListById(channels, reverse=False)
            #print "i am slave"
            #print self.slaveHoppingSequence


class HighestIdFirstExhaustiveSearch(ExhaustiveSearch):
    def __init__(self, node_id, channels, verbose):
        ExhaustiveSearch.__init__(self, "HIDFEX", node_id, channels, verbose)

        # Sort channels in decending order according to channel ID
        if self.isMaster:
            self.masterHoppingSequence = self.getSortedListById(channels, reverse=True)
        else:
            self.slaveHoppingSequence = self.getSortedListById(channels, reverse=True)


class SmallestGapFirstExhaustiveSearch(ExhaustiveSearch):
    def __init__(self, node_id, channels, verbose):
        ExhaustiveSearch.__init__(self, "SGFEX", node_id, channels, verbose)

        # Sort channels in accending order according to gap size
        if self.isMaster:
            self.masterHoppingSequence = self.getSortedListByGapSize(channels, reverse=False)
            #print "i am master"
            #print self.masterHoppingSequence
        else:
            self.slaveHoppingSequence = self.getSortedListByGapSize(channels, reverse=False)
            #print "i am slave"
            #print self.slaveHoppingSequence


class LargestGapFirstExhaustiveSearch(ExhaustiveSearch):
    def __init__(self, node_id, channels, verbose):
        ExhaustiveSearch.__init__(self, "LGFEX", node_id, channels, verbose)

        # Sort channels in decending order according to gap size
        if self.isMaster:
            self.masterHoppingSequence = self.getSortedListByGapSize(channels, reverse=True)
        else:
            self.slaveHoppingSequence = self.getSortedListByGapSize(channels, reverse=True)


class EvenOddFirstExhaustiveSearch(ExhaustiveSearch):
    def __init__(self, node_id, channels, verbose):
        ExhaustiveSearch.__init__(self, "EOFEX", node_id, channels, verbose)

        # Sort channels in decending order according to gap size
        if self.isMaster:
            self.masterHoppingSequence = self.getSortedListEvenOddFirst(channels, evenFirst=True)
            # some other variants for testing
            #self.masterHoppingSequence = self.getSortedListEvenOddFirst(channels, evenFirst=False)
            #self.masterHoppingSequence = self.getSortedListById(channels, reverse=False)
            #self.masterHoppingSequence = self.getRandomList(channels)
            #self.masterHoppingSequence = self.getSortedListEvenOddOnly(channels, evenOnly=False)
        else:
            self.slaveHoppingSequence = self.getSortedListEvenOddFirst(channels, evenFirst=False)
            # some other variants ..
            #self.slaveHoppingSequence = self.getSortedListEvenOddFirst(channels, evenFirst=True)
            #self.slaveHoppingSequence = self.getSortedListEvenOddOnly(channels, evenOnly=True)
            #print "len: %d" % len(self.slaveHoppingSequence)
            #self.slaveSecondarySequence = self.getRandomList(channels)

    def getSortedListEvenOddFirst(self, channels, evenFirst=True):
        lst = channels.getChannelIdsAsList()
        #print lst
        even = [x for x in lst if (x % 2) == 0]
        odd = [x for x in lst if (x % 2) != 0]
        #print even
        #print odd
        
        if evenFirst:       
            return (even + odd)
        else:
            return (odd + even)


    def getSortedListEvenOddOnly(self, channels, evenOnly=True):
        lst = channels.getChannelIdsAsList()
        if evenOnly:
            even = [x for x in lst if (x % 2) == 0]
            return even
        else:
            odd = [x for x in lst if (x % 2) != 0]
            return odd

