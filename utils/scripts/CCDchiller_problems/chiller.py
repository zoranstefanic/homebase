#!/usr/bin/env python2.6
from matplotlib.dates import strpdate2num
#from matplotlib.mlab import load
import numpy as np
from pylab import figure, show, grid


#Tue May 18 10:23:15 2010      17.00   14.90  68    1.59   17.00   17.50  0   0


dates, closes = np.loadtxt(
    'out', delimiter='\t',
    converters={0:strpdate2num('%a %b %d %H:%M:%S %Y')},
    skiprows=2, usecols=(0,4), unpack=True)

fig = figure()
ax = fig.add_subplot(111)
ax.plot_date(dates, closes, '-')
#ax.set_ylim((30,100))
grid()
fig.autofmt_xdate()
show()
