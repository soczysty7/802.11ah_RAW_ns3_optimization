#!/usr/bin/python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as st
import os, re

def simpleMatcher(word):
    reg1 = r'(\d{1,4}sta)'
    reg2 = r'(\d+)'
    match1 = re.search(reg1, word)
    match2 = re.search(reg2, match1[1])
    return match2[1]

class LineChartist:

    def __init__(self,resultsDir, subDirs, xaxis):
        self.basePath = resultsDir
        self.subPaths = subDirs
        self.lim = xaxis
    # mozna wyrysowac wedlug takich metryk :

    # edcaqueuelength,totalnumberofdrops,numberofmactxmissedack,numberoftransmissions,
    # NumberOfDroppedPackets,AveragePacketSentReceiveTime,PacketLoss,latency,GoodputKbit,
    # totaldozetime,EnergyRxIdle,EnergyTx

    colours=['r','g','b','k','m']
    metricToShow = ['Latency', 'PacketLoss', 'GoodputKbit', 'EnergyRxIdle', 'EnergyTx']
    prettyMetricNames = ['latency [ms]', 'packet loss [%]', 'goodput [kb/s]', 'energy in Rx and Idle [mJ]', 'energy in Tx [mJ]']
    prettyMetrics = dict(zip(metricToShow, prettyMetricNames))

    def makePlot(self, pathList, metric):
        for idx, p in enumerate(self.subPaths):
            path = self.basePath + p    
            frames = []
            for filename in os.listdir(path):
                if not filename.endswith('csv'):
                    continue
                df = pd.read_csv(os.path.join(path, filename), delimiter=';',usecols=[metric,'TrafficString'])
                if not df.empty:
                    frames.append(df)
            fr={} # mapa zaczytanych dataframow
            for j in range(0, len(frames)):
                i = simpleMatcher(frames[j]['TrafficString'][0])
                fr[i]=frames[j] # w slowniku do klucza 'nsta' wczytuje dany dataframe
            meanArr = [] # lista srednich
            nsta = [] # lista nsta - osi x
            for n in fr.keys():
                # Przygotowanie danych :
                fr[n][metric]=fr[n][metric].str.split(",")
                for i in range(0, len(fr[n][metric])):
                    for j in range(0, len(fr[n][metric][i])):
                        fr[n][metric][i][j]=float(fr[n][metric][i][j])
                    fr[n][metric][i]=fr[n][metric][i][0]
                for i in range(0, len(fr[n]['TrafficString'])):
                    a = simpleMatcher(fr[n]['TrafficString'][i])                   
                    fr[n]['TrafficString'][i]=float(a)
                fr[n]=fr[n].rename(columns={'TrafficString':'NSta'})
                fr[n]=fr[n].astype(float)
                # Analiza :
                df_nice = fr[n].groupby('NSta')[metric]
                mean = df_nice.mean()
                nsta.append(mean.index[0])
                std = df_nice.std()
                meanArr.append(mean.data[0])
                alpha=0.05
                n = df_nice.count()
                yerr = std / np.sqrt(n) * st.t.ppf(1-alpha/2, n - 1)
                # Dodanie do wykresu errorBara dla danego df:
                plt.errorbar(mean.index, mean, yerr=yerr, linestyle='',capsize=3, ecolor=self.colours[idx])
            ax = mean.plot(label='')
            ax.set(xlabel="number of stations", ylabel="Mean per-STA " + self.prettyMetrics[metric])
            nsta = np.array(nsta)
            nsta = nsta.astype(int)
            indices = np.argsort(nsta)
            sorted_array = [meanArr[indices[j]] for j in range(len(meanArr))]
            nsta.sort()
            match1 = re.search(r'(\d+)', p)
            legendOzn = match1[1] + ' slots' # uwaga na rodzaj eksperymentu       
            ax.plot(nsta, sorted_array, self.colours[idx], label=legendOzn)
            ax.legend()
        plt.xlim(self.lim)
        #plt.show(ax)
        fileName = metric + 'Stack' + '.svg'
        plt.savefig(self.basePath + fileName ,format='svg')
        plt.clf()

    def makePlotStack(self):
        for met in self.metricToShow:
            self.makePlot(self.subPaths, met)
