import numpy as np
import matplotlib.pyplot as plt
from pylab import *
from itertools import cycle

# some colors and line markers
tui_green = (0,0.455,0.478)
tui_blue = (0,0.2,0.349)
tui_orange = (1.0,0.475,0)
tui_lightblue = (0.706,0.863,0.863)
line_markers = ["-", "-s", "-^", "-D", "-o"]

class Plotter(object):
    def __init__(self, filename="dummy.dat"):
        self.colors = [tui_green, tui_blue, tui_orange]
        #self.colors = [tui_blue]
        self.colorcycler = cycle(self.colors)
        self.linecolor = next(self.colorcycler)
        self.used_colors = 0
        self.line_markers = line_markers
        self.linecycler = cycle(self.line_markers)
        self.linestyle = next(self.linecycler)
        self.xlabel = 'X'
        self.ylabel = 'Y'
        self.xlim = 0
        self.ylim = 0
        self.legendpos = 'upper right'

    def add_xaxis(self, data):
        self.x = data
        
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
            
    def set_legend_pos(self, pos):
        self.legendpos = pos

    def add_data(self, data, label='None', linestyle=None, color=tui_blue):       
        (linestyle, linecolor) = self.get_line_style_and_color()
        plt.plot(self.x, data, linestyle, linewidth=2.0, label=label, color=linecolor)
        #plt.errorbar(self.x, data, xerr=0.2, yerr=0.4)
        plt.grid=True

    def add_vertical_line(self, pos, color=tui_green, style='dashed'):
        plt.axvline(x=pos, color=color, ls=style)
        
    def get_line_style_and_color(self):
        # iterate over colors first, then use different linestyles, too
        self.linecolor = next(self.colorcycler)
        self.used_colors += 1
        if self.used_colors > len(self.colors):
            self.linestyle = next(self.linecycler)
        return (self.linestyle, self.linecolor)

    def decorate_plots(self):
        plt.legend(loc=self.legendpos, shadow=False)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.xlim(self.xlim)
        plt.ylim(self.ylim)
        
    def set_use_tex(self):
        self.decorate_plots()
        params = {'font.family': 'sans-serif',
                  'font.sans-serif': ['TeX Gyre Heros', 'Bitstream Vera Sans', 'Verdana','Tahoma'],
                  'font.size': 12,
                  'axes.labelsize': 12,
                  'text.fontsize': 12,
                  'legend.fontsize': 12,
                  'xtick.labelsize': 12,
                  'ytick.labelsize': 12,
                  'text.usetex': True}
        plt.rcParams.update(params)

    def show_plots(self):
        self.decorate_plots()
        plt.show()

    def save_plots(self, filename):
        plt.savefig(filename)

