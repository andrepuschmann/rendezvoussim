#
# This file is part of RendezvousSim. RendezvousSim is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2014 Andre Puschmann <andre.puschmann@tu-ilmenau.de>

import numpy as np

class MinMaxMonitor():
    def __init__(self):
        self.values = []
    def tally(self, x):
        self.values.append(x)
    def mean(self):
        return np.mean(self.values)
    def min(self):
        return np.min(self.values)
    def max(self):
        return np.max(self.values)
    def len(self):
        return len(self.values)
    def var(self):
        return np.var(self.values)
    def std(self):
        return np.std(self.values)
    def reset(self):
        self.values = []
    def get(self):
        return self.values


def isEqual(iterator):
      try:
         iterator = iter(iterator)
         first = next(iterator)
         return all(first == rest for rest in iterator)
      except StopIteration:
         return True


def areNeighborChannels(channels):
    assert len(channels) == 2
   
    # check upper neighbor
    if channels[0].getId() == (channels[1].getId() + 1):
        return True
    # .. and lower neighbor
    elif channels[0].getId() == (channels[1].getId() - 1):
        return True
    
    return False


def string_splitter(option, opt, value, parser):
    setattr(parser.values, option.dest, value.split(','))
