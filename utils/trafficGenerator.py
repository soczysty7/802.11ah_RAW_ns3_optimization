#!/usr/bin/python
import os
import copy
import subprocess
import errno
import numpy as np, numpy.random

class TrafficMaker:

    def __init__(self,directoryPath, TrafficPath):
        self.dp = directoryPath
        self.tp = self.dp + TrafficPath

    def genTraffic(self, staNumbers, o, t):
        # wygeneruj ruch o sumarycznej wartosci t dla stacji (tablica staNumbers) o odchyleniu o  

        for j in staNumbers: 
           trfcs = np.random.normal(np.ones(j), o)
           trfcs = trfcs/trfcs.sum()*t
           tmp = self.tp + str(j) + 'sta_sim' + '.txt'
           if not os.path.exists(os.path.dirname(tmp)):
               try:
                   os.makedirs(os.path.dirname(tmp))
               except OSError as exc:
                   if exc.errno != errno.EEXIST:
                       raise
           traffic = open(tmp, 'w')
           for z in range(0, j):
               tpt = float("{0:.8f}".format(trfcs[z]))
               traffic.write('%s	%s\n' % (str(z), str(tpt)))
           traffic.close()
