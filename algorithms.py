import numpy as np
from time import sleep



def getNextPrime(M=1):
    
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
        if is_prime(i) and M != i: break
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
            print i,
        
    def trace(self, slot=0, message=''):
        if self.verbose: print "%d: %s:\t%s" % (slot, self.name, message)        

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
        
    def trace(self, message=''):
        if self.verbose: print "   %s:\t%s" % (self.name, message)          



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

    def printSequence(self):
        print "Current rendezvous sequence for %d channels:" % self.nr_of_channels
        for i in self.sequence:
            print "%d " % i,
        print ""


class JSHoppingRendezvous(Rendezvous):
    def __init__(self, nr_of_channels):
        Rendezvous.__init__(self, "JSHopping", nr_of_channels)
        self.sequence = self.createSequence()
    
    """ this code sequence generates a full hopping sequence with 3*P^2*M slots """
    def createSequence(self):
        sequence = []
        
        # use the same parameter names for convinience 
        M = self.nr_of_channels
        P = self.getNextPrime(M)

        # i remains the same for 3*M*P time slots [1,P], round-robin afterwards (note, index here starts with 0)
        i = int(uniform(0, P - 1)) # step-length for the outer loop
        # r remains the same in each round [1,M], round-robin afterwards (note, index here starts with 0)
        r = int(uniform(0, M - 1)) # step-length for the inner loop and channel index for stay

        for l in xrange(P):
            # loop P times
            #print "i: %d" % (i + 1)
            for s in xrange(M):
                # loop M times
                #print "  r: %d" % (r + 1)
                round = self.JSHopping(M, P, r + 1, i + 1) # create one round, adjust index numbers
                sequence.extend(round)
                #print round
                r = (r + 1) % M
                
            i = (i + 1) % P
        
        # cleanup sequence to make sure the channel index starts with 0        
        for i in xrange(len(sequence)):
            sequence[i] = sequence[i] - 1
        
        #print sequence
        
        # finally return sequence
        return sequence

    # Generate one round JS hopping sequence for the given paramaters
    def JSHopping(self, M, P, r, i):        
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
                
            nextround.append(j)
        return nextround
