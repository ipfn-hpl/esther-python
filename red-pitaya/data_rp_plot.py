#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 09 12:11:30 2021

@author: Bernardo Carvalho
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
import wavio

if len(sys.argv) > 1:
    filename = str(sys.argv[1])
else:
    filename = 'data_file_2020-10-09_18-44-32'

DECIMATION = 8
FREQ_SAMP = 125.0e3/DECIMATION  # (in kHz)
data_raw = wavio.read(filename + '.wav')

ch0 = data_raw.data / 2**13
time = np.arange(ch0.size)/FREQ_SAMP

fig, ax = plt.subplots()

ax.plot(time, ch0, label='Channel 0')
ax.set_ylabel('V / V')
ax.set_xlabel('Time/ms')
ax.set_title("Red Pitaya Kistler")  # Add a title to the axes.
ax.legend(loc='upper left')  # Add a legend.
plt.savefig(filename + '.png')
plt.show()
