#!/usr/bin/python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as st
import os
# Wczytaj tylko wlasciwe kolumny :

path = '/home/soczysty7/Mgr_2019/8LipcaClone/per_contention_charts/4c'
frames = []
for filename in os.listdir(path):
    if not filename.endswith('csv'):
        continue
    #if filename.startswith('1S'):
    #    continue
    df = pd.read_csv(os.path.join(path, filename), delimiter=';',usecols=['GoodputKbit','TrafficString'])
    frames.append(df)
    
#/home/soczysty7/Mgr_2019/8LipcaClone/IEEE-802.11ah-ns-3/OptimalRawGroup/traffic/16sta_sim.txt
fr={} # Slownik zaczytanych dataframow - bedzie potrzebny zeby nie miec miliona zmiennych
for j in range(0, len(frames)):
    if (len(frames[j]['TrafficString'][0]) == 93): # 2 cyfrowa liczba stacji
        i=frames[j]['TrafficString'][0][-13:-11]
    elif (len(frames[j]['TrafficString'][0]) == 94): # 3 cyfrowa liczba stacji
        i=frames[j]['TrafficString'][0][-14:-11]
    fr[i]=frames[j] # w slowniku do klucza 'nsta' wczytuje dany dataframe

for n in fr.keys(): #

    # Przygotowanie danych :

    fr[n]['GoodputKbit']=fr[n]['GoodputKbit'].str.split(",")

    for i in range(0, len(fr[n]['GoodputKbit'])):
        for j in range(0, len(fr[n]['GoodputKbit'][i])):
            fr[n]['GoodputKbit'][i][j]=float(fr[n]['GoodputKbit'][i][j])
        fr[n]['GoodputKbit'][i]=np.mean(fr[n]['GoodputKbit'][i])

    for i in range(0, len(fr[n]['TrafficString'])):
        if (len(fr[n]['TrafficString'][i]) == 93):
            a = fr[n]['TrafficString'][i][-13:-11]
        elif (len(fr[n]['TrafficString'][i]) == 94):
            a = fr[n]['TrafficString'][i][-14:-11]
        fr[n]['TrafficString'][i]=float(a)

    fr[n]=fr[n].rename(columns={'TrafficString':'NSta'})
    fr[n]=fr[n].astype(float)

    # Analiza :

    df_nice = fr[n].groupby('NSta')['GoodputKbit']
    mean = df_nice.mean()
    std = df_nice.std()

    alpha=0.05
    n = df_nice.count()
    yerr = std / np.sqrt(n) * st.t.ppf(1-alpha/2, n - 1)

    # Dodanie do wykresu słupka dla danego df:

    ax = mean.plot(title='4 STA per slot', yerr=yerr)
    ax.set(xlabel="NSta", ylabel="Mean Per STA GoodputKbit")
    ax=plt.errorbar(mean.index, mean, yerr=yerr, linestyle='',capsize=3)
    ax=plt.bar(mean.index, mean, width=3)
    #ax.plot(mean.index, mean, 'b-') #kropeczki chociaż rysować :)
    # x = np.linspace(0, 10*np.pi, 100)
    # y = np.sin(x)
    # ax.plot(x, y, 'b-')
plt.xlim(0,176,16)
plt.show(ax)
#plt.savefig('late4.png',format='png')
#plt.savefig('N_STA_2Mhz_MCS8.svg',format='svg')