#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 13:07:11 2013

 File layout:
 alg	M	G	num_it	num_ok	num_nok	TTRmin	TTRmean	TTRmax	TTRstd
 ...
 
 Resulting dtype: 
 dtype=[('alg','|S10'),
                  ('max_num_channels','i8'),
                  ('num_overlapping_channels','i8'),
                  ('num_it','i8'),
                  ('num_it_ok','i8'),
                  ('num_it_nok','i8'),
                  ('ttr_min','f8'),
                  ('ttr_mean','f8'),
                  ('ttr_max','f8'),
                  ('ttr_std','f8')],

"""

import numpy as np
import pylab as pl

from plotter import Plotter
import sys
from optparse import OptionParser

labels = {"random":"Random",
          "js":"Jump-Stay",
          "crseq":"CRSEQ"}

def main():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("--ttr", dest="ttr", default=False, action="store_true",
                      help="Whether to plot mean TTR")
    parser.add_option("--mttr", dest="mttr", default=False, action="store_true",
                      help="Whether to plot maximum TTR")
    parser.add_option("--tex", dest="usetex", default=False, action="store_true",
                      help="Whether to TeX for output")
    parser.add_option("-i", "--input", dest="infile",
                      help="Read from file", metavar="FILE")
    parser.add_option("-o", "--output", dest="outfile",
                      help="Write output to file", metavar="FILE")

    
    # turn command line parameters into local variables
    (options, args) = parser.parse_args()
    ttr = options.ttr
    mttr = options.mttr
    infile = options.infile
    outfile = options.outfile
    usetex = options.usetex
    
    # Read values
    data = np.genfromtxt(infile,
                          dtype=[('alg','|S10'),
                      ('max_num_channels','i8'),
                      ('num_overlapping_channels','i8'),
                      ('num_it','i8'),
                      ('num_it_ok','i8'),
                      ('num_it_nok','i8'),
                      ('ttr_min','f8'),
                      ('ttr_mean','f8'),
                      ('ttr_max','f8'),
                      ('ttr_std','f8')],
                         delimiter='\t', skip_header=1, skip_footer=0,
                         )
    
    # Extract general variables
    max_num_channels = data['max_num_channels'][0]
    #print "max_num_channels: %d" % max_num_channels
    
    # Extract algorithms in result file
    algorithms = []
    for x in data['alg']:
        if x not in algorithms:
            algorithms.append(x)
            
    # Extract samples for each algorithm
    mean_values = {}
    max_values = {}
    num_overlapping_channels = 0
    for alg in algorithms:
        raw_samples = [x for x in data if x['alg'] == alg]
        mean_values[alg] = [x[7] for x in raw_samples] # mean values are in column 8
        max_values[alg] = [x[8] for x in raw_samples] # max values are in column 9
        num_overlapping_channels = [x[2] for x in raw_samples] # should be the same for all
    
    #print mean_values['random']
    #print num_overlapping_channels
    
    
    plot = Plotter()
    plot.add_xaxis(num_overlapping_channels)
    
    if ttr:
        # Plot mean value for each algorithm
        for alg in algorithms:
            plot.add_data(mean_values[alg], label=labels[alg])
        plot.set_axis_labels('Overlapping channels', 'E[TTR]')
        #plot.set_axis_lim([1,20], [0,2500])
    elif mttr:
        # Plot max value for each algorithm
        for alg in algorithms:
            plot.add_data(max_values[alg], label=labels[alg])
        plot.set_axis_labels('Overlapping channels', 'MTTR')
        #plot.set_axis_lim([1,20])
        plot.set_legend_pos('upper right')

    if usetex:
        plot.set_use_tex()

    if outfile:
        plot.save_plots(outfile)
        
    if not usetex:
        plot.show_plots()

if __name__ == "__main__":
    main()
