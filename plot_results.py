#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 13:07:11 2013

 File layout:
 alg  M  G  num_it  num_ok  num_nok  TTRmin  TTRmean  TTRmax  TTRstd  bw  acdp  theta
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
                  ('ttr_std','f8'),
                  ('bw','i8'),
                  ('acdp','f8'),
                  ('theta','f8')]],

"""

import numpy as np
import pylab as pl
from plotter import Plotter
import sys
from optparse import OptionParser
from helper import string_splitter

labels = {"random":"Random",
          "js":"Jump-Stay",
          "crseq":"CRSEQ",
          "mc":"Modular Clock",
          "ex":"Exhaustive Search"}

def get_label(alg):
    try:
        return labels[alg]
    except:
        return alg


def main():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    #parser.add_option("-m", "--model", dest="model", default="symmetric",
    #                  help="Which channel model to use (symmetric or asymmetric)")
    parser.add_option("-x", dest="x", default=None, type='string',
                      help="Which values to use for x axis (options are: max_num_channels, num_overlapping_channels, bw)")
    parser.add_option("-y", dest="y", default=None, type='string',
                      help="Which values to use for y axis (options are: ttr, mttr)")
    parser.add_option("--tex", dest="usetex", default=False, action="store_true",
                      help="Whether to TeX for output")
    parser.add_option("-i", "--input", dest="infile",
                      help="Read from file", metavar="FILE")
    parser.add_option("-o", "--output", dest="outfile",
                      help="Write output to file", metavar="FILE")
    parser.add_option("-a", "--algorithm", dest="algorithm",
                      help="Which rendezvous algorithm to include in plot",
                      type='string', action='callback', callback=string_splitter)


    # turn command line parameters into local variables
    (options, args) = parser.parse_args()
    #model = options.model
    x_axis_param = options.x
    y_axis_param = options.y
    infile = options.infile
    outfile = options.outfile
    usetex = options.usetex
    algs_asked_to_plot = options.algorithm

    # Stop if x,y and input are not given
    #print x_axis_param
    
    if (not x_axis_param) or (not y_axis_param) or (not infile):
        parser.error("Incorrect number of arguments")

    # Read values
    data = np.genfromtxt(infile, comments="#", delimiter='\t',
                          dtype=[('alg','|S10'),
                      ('max_num_channels','i8'),
                      ('num_overlapping_channels','i8'),
                      ('num_it','i8'),
                      ('num_it_ok','i8'),
                      ('num_it_nok','i8'),
                      ('ttr_min','f8'),
                      ('ttr_mean','f8'),
                      ('ttr_max','f8'),
                      ('ttr_std','f8'),
                      ('bw','i8'),
                      ('acdp','f8'),
                      ('theta','f8')]
                         )
    
    valid_x_values = ['max_num_channels', 'num_overlapping_channels', 'bw']
    valid_y_values = ['ttr', 'mttr']
    
    # check if x and y are valid options
    if x_axis_param not in valid_x_values:
        print "%s is not a valid option as x value." % x
        sys.exit()
        
    if y_axis_param not in valid_y_values:
        print "%s is not a valid option as y value." % x
        sys.exit()
   
    # Extract values for x axis, num_overlapping_channels can be
    # used for both symmetric and assymetric results
    raw_x = data[x_axis_param]
    
    # .. remove duplets
    x_values = []
    for val in raw_x:
        if val not in x_values:
            x_values.append(val)
    min_x_value = x_values[0]
    max_x_value = x_values[-1]
    
    #print raw_x

    #print len(x_values)
    #print x_values

    # Extract algorithms in result file
    algs_to_plot = []
    for x in data['alg']:
        if x not in algs_to_plot:
            if (algs_asked_to_plot == None) or (x in algs_asked_to_plot):
                algs_to_plot.append(x)
            
    # Extract samples for each algorithm
    mean_values = {}
    max_values = {}
    for alg in algs_to_plot:
        raw_samples = [x for x in data if x['alg'] == alg]
        mean_values[alg] = [x[7] for x in raw_samples] # mean values are in column 8
        #print len(mean_values[alg])
        max_values[alg] = [x[8] for x in raw_samples] # max values are in column 9
    
    plot = Plotter()   
    plot.add_xaxis(x_values)
    plot.set_axis_lim([min_x_value, max_x_value])
    plot.set_xticks(min_x_value, max_x_value + 1, 1)

    if x_axis_param == 'max_num_channels':
        plot.set_axis_labels('Total number of channels')
        plot.set_legend_pos('upper left')    
    elif x_axis_param == 'num_overlapping_channels':
        plot.set_axis_labels('Number of overlapping channels')
        plot.set_legend_pos('upper right')
    elif x_axis_param == 'bw':
        plot.set_axis_labels('Average channel block width')
        plot.set_legend_pos('upper left')
    
    if y_axis_param == 'ttr':
        # Plot mean value for each algorithm
        for alg in algs_to_plot:
            plot.add_data(mean_values[alg], label=get_label(alg))
        plot.set_axis_labels(None, 'E[TTR]')
        #plot.set_axis_lim([1,20], [0,2500])
    elif y_axis_param == 'mttr':
        # Plot max value for each algorithm
        for alg in algs_to_plot:
            plot.add_data(max_values[alg], label=get_label(alg))
        plot.set_axis_labels(None, 'MTTR')

    if usetex:
        plot.set_use_tex()

    if outfile:
        plot.save_plots(outfile)
        
    if not usetex:
        plot.show_plots()

if __name__ == "__main__":
    main()
