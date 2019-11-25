#!/usr/bin/python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as st
import os

text = True
simName = 'sumaryczne'
path = '/home/soczysty7/Mgr19/Results/RCA/new/'

for filename in os.listdir(path):
    if not filename.endswith('.nss'):
        continue
    if ( text ) :
        full_path = os.path.join(path, filename)
        good_words = ['nodestats', 'nodestatsheader']
        with open(full_path) as oldfile, open('newfile.txt', 'w') as newfile:
            for line in oldfile:
                if any(good_word in line for good_word in good_words):
                    if  '0;nodestatsheader;' in line :
                        line = line.replace('0;nodestatsheader;', 'TIMESTAMP;nodestatsheader;')
                    newfile.write(line)

    df = pd.read_csv('newfile.txt', delimiter=';', usecols=['GoodputKbit','TIMESTAMP'])
    prevv = list(range(-700, 0, 200))
    nextt = list(range(0, 1600, 200))
    t = df['TIMESTAMP'].astype(float)/1000000000
    g = df['GoodputKbit'].astype(float)/1000
    
    ax = plt.subplot()
    ax.set_xticklabels(prevv + nextt)
    ax.plot(t, g, label=os.path.splitext(filename)[0])
    ax.legend()

    ax.set(xlabel='Distance from AP', ylabel='Throughput [Mb/s]')
    ax.grid()

plt.savefig(path + simName + '.svg', format='svg')
# plt.show()