#!/usr/bin/python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as st
import os
# Wczytaj tylko wlasciwe kolumny :

text = True

if ( text ) :

    path = '/home/soczysty7/Mgr_2019/Results/RCA/'
    #filename = 'constant_rate_mcs2_seed1.nss'
    filename = 'minstrel_mcs2_seed1.nss'
    full_path = os.path.join(path, filename)

    good_words = ['nodestats', 'nodestatsheader']

    with open(full_path) as oldfile, open('newfile.txt', 'w') as newfile:
        for line in oldfile:
            if any(good_word in line for good_word in good_words):
                if  '0;nodestatsheader;' in line :
                    line = line.replace('0;nodestatsheader;', 'TIMESTAMP;nodestatsheader;')
                newfile.write(line)


df = pd.read_csv('newfile.txt', delimiter=';', usecols=['GoodputKbit','TIMESTAMP'])
t = df['TIMESTAMP'].astype(int)/1000000000
g = df['GoodputKbit'].astype(float)/1000

fig, ax = plt.subplots()

print(t,g)
ax.plot(t, g)

ax.set(xlabel='Distance from start', ylabel='GoodputKbit',
       title='Minstrel')
ax.grid()

#fig.savefig("minstrel_niewyszlo.png")
#fig.savefig("constant_niewyszlo.png")

plt.show()