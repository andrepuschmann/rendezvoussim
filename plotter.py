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
import matplotlib.pyplot as plt
from pylab import *
from itertools import cycle

# some colors and line markers
line_markers = ["-", "-s", "-^", "-D", "-o"]
line_markers = ["-", "--", "-.", ":", "."]



class Plotter(object):
    def __init__(self, filename="dummy.dat"):
        self.colors = ['blue', 'red', 'green']
        self.colorcycler = cycle(self.colors)
        self.linecolor = next(self.colorcycler)
        self.used_colors = 0
        self.line_markers = line_markers
        self.linecycler = cycle(self.line_markers)
        self.linestyle = next(self.linecycler)
        self.xlabel = 'X'
        self.ylabel = 'Y'
        self.title = ''
        self.xlim = 0
        self.ylim = 0
        self.legendpos = 'upper right'
        self.fig = plt.figure(1)
        self.ax = self.fig.add_subplot(111)
        self.ax.patch.set_alpha(0.3)
        self.ax.patch.set_facecolor('white')
        #ax.patch.set_facecolor('0.9')

    def add_xaxis(self, data):
        self.x = data
        
    def set_title(self, title):
        self.title = title
        
    def set_axis_labels(self, x=None, y=None):
        if x:        
            self.xlabel = x
        if y:
            self.ylabel = y
        
    def set_axis_lim(self, x=None, y=None):
        if x:        
            self.xlim = x
        if y:
            self.ylim = y
            
    def set_xticks(self, start, stop, stepsize):
        self.xtick_start = start
        self.xtick_stop = stop
        self.xtick_stepsize = stepsize
        plt.xticks(np.arange(self.xtick_start, self.xtick_stop, self.xtick_stepsize))
            
    def set_legend_pos(self, pos):
        self.legendpos = pos

    def add_data(self, data, label='None', linestyle=None, color='blue'):       
        (linestyle, linecolor) = self.get_line_style_and_color()
        plt.plot(self.x, data, linestyle, linewidth=2.0, label=label, color=linecolor)
        #plt.errorbar(self.x, data, xerr=0.2, yerr=0.4)
        plt.grid=True

    def add_vertical_line(self, pos, color='black', style='dashed'):
        plt.axvline(x=pos, color=color, ls=style)
        
    def get_line_style_and_color(self):
        # iterate over colors first, then use different linestyles, too
        self.linecolor = next(self.colorcycler)
        self.used_colors += 1
        if self.used_colors > len(self.colors):
            self.linestyle = next(self.linecycler)
        return (self.linestyle, self.linecolor)

    def decorate_plots(self):
        legend = plt.legend(loc=self.legendpos, shadow=False)
        frame = legend.get_frame()
        frame.set_facecolor('0.90')
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.xlim(self.xlim)
        plt.ylim(self.ylim)
        self.ax.set_title(self.title)
        
    def set_use_tex(self):
        self.decorate_plots()
        params = {'font.family': 'sans-serif',
                  'font.sans-serif': ['TeX Gyre Heros', 'Bitstream Vera Sans', 'Verdana','Tahoma'],
                  'font.size': 9,
                  'axes.labelsize': 9,
                  'text.fontsize': 9,
                  'legend.fontsize': 9,
                  'xtick.labelsize': 9,
                  'ytick.labelsize': 9,
                  'text.usetex': True}
        plt.rcParams.update(params)

    def set_size(self, width, height):
        self.fig.set_size_inches(width / 2.54 / 10, height / 2.54 / 10)

    def show_plots(self):
        self.decorate_plots()
        plt.show()

    def save_plots(self, filename):
        plt.savefig(filename)

