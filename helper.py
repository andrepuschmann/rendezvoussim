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
