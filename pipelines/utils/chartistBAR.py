#!/usr/bin/python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as st
import os, re
path = '/home/soczysty7/Mgr19/Results/STATIC/DEBUG_plots/'
frames = []
metricToShow = ['Latency', 'PacketLoss', 'GoodputKbit', 'EnergyRxIdle', 'EnergyTx']
metric = metricToShow[2]

def simpleMatcher(word):
    reg1 = r'(\d{1,4}sta)'
    reg2 = r'(\d+)'
    match1 = re.search(reg1, word)
    match2 = re.search(reg2, match1[1])
    return match2[1]

for filename in os.listdir(path):
    if not filename.endswith('csv'):
        continue
    df = pd.read_csv(os.path.join(path, filename), delimiter=';',usecols=[metric,'TrafficString'])
    frames.append(df) 
fr={}
for j in range(0, len(frames)):
    i = simpleMatcher(frames[j]['TrafficString'][0])
    fr[i]=frames[j]
for n in fr.keys():
    fr[n][metric]=fr[n][metric].str.split(",")
    for i in range(0, len(fr[n][metric])):
        for j in range(0, len(fr[n][metric][i])):
            fr[n][metric][i][j]=float(fr[n][metric][i][j])
        fr[n][metric][i]=np.mean(fr[n][metric][i])

    for i in range(0, len(fr[n]['TrafficString'])):
        a = simpleMatcher(fr[n]['TrafficString'][i])                   
        fr[n]['TrafficString'][i]=float(a)

    fr[n]=fr[n].rename(columns={'TrafficString':'NSta'})
    fr[n]=fr[n].astype(float)
    df_nice = fr[n].groupby('NSta')[metric]
    mean = df_nice.mean()
    std = df_nice.std()
    alpha=0.05
    n = df_nice.count()
    yerr = std / np.sqrt(n) * st.t.ppf(1-alpha/2, n - 1)
    ax = mean.plot(title='4 STA per slot', yerr=yerr)
    ax.set(xlabel="NSta", ylabel="Mean Per STA GoodputKbit")
    ax=plt.errorbar(mean.index, mean, yerr=yerr, linestyle='',capsize=3)
    ax=plt.bar(mean.index, mean, width=3)
plt.xlim(0,210,10)
plt.show(ax)
#plt.savefig('late4.png',format='png')
#plt.savefig('N_STA_2Mhz_MCS8.svg',format='svg')