#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 09 12:11:30 2021

@author: Bernardo Carvalho
"""

import sys
import numpy as np
# import matplotlib.pyplot as plt
import wavio
# import pandas as pd

if len(sys.argv) > 1:
    filename = str(sys.argv[1])
else:
    filename = 'data_file_2020-10-09_18-44-32'

NUM_CHANNELS = 32

data_raw = wavio.read(filename + '.wav')

ch0 = np.array(data_raw.data, dtype=np.int16)

np.savetxt(filename + '.csv', ch0, fmt='%d')

# df=pd.DataFrame(ch0, dtype=np.int16, columns=['ch0'])
# df.to_csv(filename + '.csv')
