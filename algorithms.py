import numpy as np
from time import sleep
import sys


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
    def __init__(self, name, nr_of_channels, verbose=True):
        self.name = name
        self.nr_of_channels = int(nr_of_channels)
        self.sequence = []
        self.index = 0
        self.verbose = verbose
 
    def getName(self):
        return self.name
        
    def getStayTime(self):
        return 1

    """ returns channel number at current index in sequence """
    def getNextIndex(self):
        r = self.sequence[self.index]
        self.index = (self.index + 1) % len(self.sequence)
        return(r)
        
    def printSequence(self):
        print "Current rendezvous sequence (len=%d) for %d channels:" % (len(self.sequence), self.nr_of_channels)
        for i in self.sequence:
            print "%d " % i,
        print ""
        
    def trace(self, message=''):
        if self.verbose: print "   %s:\t%s" % (self.name, message)           

    def __str__(self):
        return "%s is!!!" % (self.name)


class RandomRendezvous(Rendezvous):
    def __init__(self, nr_of_channels, verbose):
        Rendezvous.__init__(self, "Random", nr_of_channels, verbose)
    
    """ override base class function, return random channel number between 0 and number of channels """
    def getNextIndex(self):
        #print "nr of channels: %d" % self.nr_of_channels
        r = np.random.randint(0, self.nr_of_channels) # draw random number between 0 and nr_of_channels
        #print "rand: %d" % r
        return(r)



class ModularClockRendezvous(Rendezvous):
    def __init__(self, nr_of_channels, verbose):
        Rendezvous.__init__(self, "ModularClock", nr_of_channels, verbose)
        self.nr_of_channels = int(nr_of_channels)
        self.p = getNextPrime(self.nr_of_channels)
        self.j_old = np.random.randint(0, self.nr_of_channels) # pick first channel randomly
        self.renew_rate()
        self.current_slot = 1
        self.trace("prime: %d" % self.p)
        self.trace("j_old: %d" % self.j_old)        

    def renew_rate(self):
        self.r = np.random.randint(0, self.p) # pick hopping "rate"
        self.trace("rate: %d" % self.r)
    
    def getNextIndex(self):
        # renew rate every 2*p slots
        self.trace("Currslot: %d" % self.current_slot)
        if self.current_slot > (2*self.p):
            self.renew_rate()
            self.current_slot = 1
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
        return c

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
        self.trace(0, "Start index: %d" % self.index)

    
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
    def __init__(self, nr_of_channels, verbose):
        Rendezvous.__init__(self, "JSHopping", nr_of_channels, verbose)
        
        # initialize algorithm
        self.M = int(nr_of_channels)
        self.P = getNextPrime(self.M)
        self.r = np.random.randint(1, self.M + 1)
        self.i = np.random.randint(1, self.P + 1)
        self.t = 0 # current time slot
        #self.test1()

    # Simple functional test using the parameter given in the paper
    def test(self):
        print "JSPattern test"
        M = 4
        r = 1
        i = 3
        P = getNextPrime(M)
        round = self.JSHopping(M, P, r, i)
        print round

    def update_r(self):
        self.r = ((self.r + 1) % (self.M + 1))
        if self.r == 0: self.r = 1
        self.trace("New r: %d" % self.r)

    def update_i(self):
        self.i = ((self.i + 1) % (self.M + 1))
        if self.i == 0: self.i = 1
        self.trace("New i: %d" % self.i)
    
    # Just call JumpStay here
    def getNextIndex(self):
        c = self.JumpStay()
        # in simulation, channels start with index 0, do remapping
        c -= 1
        return c
        
    # Technically, this is the inner loop of the JS_2 algorithm
    def JumpStay(self):
        # Update r every 3*P time slots
        if (self.t % (3 * self.P)) == 0:
            self.trace("Update r in this round")
            self.update_r()
        # Update i every 3*M*P slots
        if (self.t % (3 * self.M * self.P)) == 0:
            self.trace("Update i in this round")
            self.update_i()
        
        # get channel for this specific slot
        c = self.JSHopping(self.M, self.P, self.r, self.i, self.t)
        self.trace("Slot: %d" % self.t)
        self.trace("CH Index: %d" % c)
        self.t += 1 # increment slot counter
        return c

    # Generate one round JS hopping sequence for the given paramaters
    def JSHopping(self, M, P, r, i, slot=-1):
        nextround = []
        for t in range(3*P):
            t = t % (3*P)   # each round takes 3P timeslots
            if t < (2*P):
                # jump pattern
                j = ((i + t*r -1) % P) + 1
            else:
                # stay pattern
                j = r
            if (j > M):
                l = j
                j = ((j - 1) % M) + 1 # remapping
                
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
    def __init__(self, nr_of_channels, verbose):
        Rendezvous.__init__(self, "CRSEQ", nr_of_channels, verbose)
        # initialize algorithm
        self.M = int(nr_of_channels)
        self.P = getNextPrime(self.M)
        self.t = 0 # current time slot
        self.trace("self.M: %d" % self.M)
        self.trace("self.P: %d" % self.P)
        #self.test2()

    # Simple functional test using the parameter given in the paper
    def test(self):
        print "CRSEQPattern test"
        M = 20
        print "M: %d" % M
        P = getNextPrime(M)
        print "P: %d" % P
        
        # Run CRSEQ for 3*M slots
        seq = []
        for i in range(3*P-1):
            c = self.CRSEQHopping(M, P, i)
            seq.append(c)
        print seq
        sys.exit()
        
    def test2(self):
        print "CRSEQ test"
        M = 20
        print "M: %d" % M
        P = getNextPrime(M)
        print "P: %d" % P        
        c = self.CRSEQHopping(M, P, 739674)
        print c
        sys.exit()
        
    
    def getNextIndex(self):
        c = self.CRSEQHopping(self.M, self.P, self.t)
        self.t += 1
        self.trace("Next channel index: %d" % c)
        return c

    def CRSEQHopping(self, M, P, slot):
        self.trace("-----")
        self.trace("M: %d" % M)
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
            return Tj % M
        else:
            return j % M
