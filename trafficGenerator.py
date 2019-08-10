#!/usr/bin/python
import os
import copy
import subprocess
import errno
import numpy as np, numpy.random

# t = 3.0
# o = 0.5
# n = 4
# m = 56
# 
# directoryPath = "/home/soczysty7/Mgr_2019/8LipcaClone/IEEE-802.11ah-ns-3/"
# TrafficPath = 'OptimalRawGroup/traffic/'

class TrafficMaker:

    def __init__(self,directoryPath, TrafficPath):
        self.dp = directoryPath
        self.tp = self.dp + TrafficPath

    def genTraffic(self, n,m,o,t):
        #print("Witam w generatorze ruchu :)")
        ### interactive mode :

        # t = input('Sumaryczny tpt w Mbps: ') # np 3.0
        # o = input('Odchylenie standardowe ruchu stacji : ') # np 0.1
        # n = input('Ile stacji per symulacja (rowniez krok) : ') # np 16
        # m = input('Max liczba stacji : ') # np 160


        # wygeneruj ruch o sumarycznej wartosci t dla n stacji o odchyleniu o
        # zrob to dla liczby stacji z zakresu od n do m co krok n        

        for j in range(n, m+n, n): 
           # mean and standard deviation
           trfcs = np.random.normal(np.ones(j), o)
           trfcs = trfcs/trfcs.sum()*t
           tmp = self.tp + str(j) + 'sta_sim' + '.txt'
           if not os.path.exists(os.path.dirname(tmp)):
               try:
                   os.makedirs(os.path.dirname(tmp))
               except OSError as exc:  # Guard against race condition
                   if exc.errno != errno.EEXIST:
                       raise
           traffic = open(tmp, 'w')
           for z in range(0, j):
               # print(n,m,k,j,z)
               tpt = float("{0:.8f}".format(trfcs[z]))
               traffic.write('%s	%s\n' % (str(z), str(tpt)))
           traffic.close()
        # ----------------------------
    def xdPRingter(self):
        print('XDDDDD')
