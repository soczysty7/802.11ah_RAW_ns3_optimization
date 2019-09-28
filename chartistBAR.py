#!/usr/bin/python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as st
import os, re
# Wczytaj tylko wlasciwe kolumny :

#path = '/home/soczysty7/Mgr_2019/8LipcaClone/per_contention_charts/4c'
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
    #if filename.startswith('1S'):
    #    continue
    df = pd.read_csv(os.path.join(path, filename), delimiter=';',usecols=[metric,'TrafficString'])
    frames.append(df)
    
#/home/soczysty7/Mgr_2019/8LipcaClone/IEEE-802.11ah-ns-3/OptimalRawGroup/traffic/16sta_sim.txt


fr={} # Slownik zaczytanych dataframow - bedzie potrzebny zeby nie miec miliona zmiennych
for j in range(0, len(frames)):
    i = simpleMatcher(frames[j]['TrafficString'][0])
    fr[i]=frames[j] # w slowniku do klucza 'nsta' wczytuje dany dataframe

for n in fr.keys(): #

    # Przygotowanie danych :

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

    # Analiza :

    df_nice = fr[n].groupby('NSta')[metric]
    mean = df_nice.mean()
    std = df_nice.std()

    alpha=0.05
    n = df_nice.count()
    yerr = std / np.sqrt(n) * st.t.ppf(1-alpha/2, n - 1)

    # Dodanie do wykresu slupka dla danego df:

    ax = mean.plot(title='4 STA per slot', yerr=yerr)
    ax.set(xlabel="NSta", ylabel="Mean Per STA GoodputKbit")
    ax=plt.errorbar(mean.index, mean, yerr=yerr, linestyle='',capsize=3)
    ax=plt.bar(mean.index, mean, width=3)
    #ax.plot(mean.index, mean, 'b-') #kropeczki chociaz rysowac :)
    # x = np.linspace(0, 10*np.pi, 100)
    # y = np.sin(x)
    # ax.plot(x, y, 'b-')
plt.xlim(0,210,10)
plt.show(ax)
#plt.savefig('late4.png',format='png')
#plt.savefig('N_STA_2Mhz_MCS8.svg',format='svg')