#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 09 12:11:30 2021

@author: Bernardo Carvalho
"""

import sys
# import numpy as np
import matplotlib.pyplot as plt
import wavio

if len(sys.argv) > 1:
    filename = str(sys.argv[1])
else:
    filename = 'data_file_2020-10-09_18-44-32'


data_raw = wavio.read(filename + '.wav')

ch0 = data_raw.data

fig, ax = plt.subplots()

ax.plot(ch0, label='Channel 0')
ax.set_ylabel('LSB')
ax.set_title("ATCA v2 32 bit data")  # Add a title to the axes.
ax.legend(loc='upper left')  # Add a legend.
plt.savefig(filename +'.png')
plt.show()
