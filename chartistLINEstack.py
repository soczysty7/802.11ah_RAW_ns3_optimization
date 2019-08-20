#!/usr/bin/python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as st
import os

class LineChartist:

    def __init__(self,resultsDir, subDirs, xaxis):
        self.basePath = resultsDir
        self.subPaths = subDirs
        self.lim = xaxis

    # Wczytaj tylko wlasciwe kolumny :

    colours=['r','g','b','k', 'm']
    metricToShow = ['Latency', 'PacketLoss', 'GoodputKbit', 'EnergyRxIdle', 'EnergyTx']

    # stats=edcaqueuelength,totalnumberofdrops,numberofmactxmissedack,numberoftransmissions,
    # NumberOfDroppedPackets,AveragePacketSentReceiveTime,PacketLoss,latency,GoodputKbit,
    # totaldozetime,EnergyRxIdle,EnergyTx \

    #TODO pozamieniac ladnie na funkcje

    def makePlot(self, pathList, metric):

        for idx, p in enumerate(self.subPaths):

            path = self.basePath + p    
            frames = []
            for filename in os.listdir(path):
                if not filename.endswith('csv'):
                    continue
                #if filename.startswith('1S'):
                #    continue
                print(os.path.join(path, filename))
                df = pd.read_csv(os.path.join(path, filename), delimiter=';',usecols=[metric,'TrafficString'])
                if not df.empty:
                    print(df)
                    frames.append(df)

            fr={} # Slownik zaczytanych dataframow - bedzie potrzebny zeby nie miec miliona zmiennych
            for j in range(0, len(frames)):
                if (len(frames[j]['TrafficString'][0]) == 78): # 1 cyfrowa liczba stacji
                    i=frames[j]['TrafficString'][0][-12:-11]  # 78 92
                if (len(frames[j]['TrafficString'][0]) == 79): # 2 cyfrowa liczba stacji
                    i=frames[j]['TrafficString'][0][-13:-11]  #79 93
                if (len(frames[j]['TrafficString'][0]) == 80): # 3 cyfrowa liczba stacji
                    i=frames[j]['TrafficString'][0][-14:-11] # 80 94
                elif (len(frames[j]['TrafficString'][0]) == 81): # 4 cyfrowa liczba stacji
                    i=frames[j]['TrafficString'][0][-15:-11] # 81 95
                # i = float(frames[j]['NSta'][0]) + 1
                # i = str(i)
                fr[i]=frames[j] # w slowniku do klucza 'nsta' wczytuje dany dataframe

            meanArr = [] #lista srednich
            nsta = [] # lista nsta - osi x

            for n in fr.keys(): #

                # Przygotowanie danych :

                fr[n][metric]=fr[n][metric].str.split(",")

                for i in range(0, len(fr[n][metric])):
                    for j in range(0, len(fr[n][metric][i])):
                        fr[n][metric][i][j]=float(fr[n][metric][i][j])
                    fr[n][metric][i]=np.mean(fr[n][metric][i])
                                                                # prosze zrob cos z tymi sciezkami
                for i in range(0, len(fr[n]['TrafficString'])):
                    if (len(fr[n]['TrafficString'][i]) == 78): # 78 92
                        a = fr[n]['TrafficString'][i][-12:-11]   #nie kombinowac z tym trafficstringiem wystarczy Nsta +1
                    if (len(fr[n]['TrafficString'][i]) == 79): # 79 93
                        a = fr[n]['TrafficString'][i][-13:-11]
                    if (len(fr[n]['TrafficString'][i]) == 80): # 80 94
                        a = fr[n]['TrafficString'][i][-14:-11]
                    elif (len(fr[n]['TrafficString'][i]) == 81): # 81 95
                        a = fr[n]['TrafficString'][i][-15:-11]
                    fr[n]['TrafficString'][i]=float(a)

                fr[n]=fr[n].rename(columns={'TrafficString':'NSta'})
                fr[n]=fr[n].astype(float)

                # Analiza :

                df_nice = fr[n].groupby('NSta')[metric]
                mean = df_nice.mean()
                meanArr.append(mean.data[0])
                nsta.append(mean.index[0])
                std = df_nice.std()

                alpha=0.05
                n = df_nice.count()
                yerr = std / np.sqrt(n) * st.t.ppf(1-alpha/2, n - 1)

                # Dodanie do wykresu errorBara dla danego df:
                    # todo usunac dodawanie legend errorbarom
                #plt.errorbar(mean.index, mean, yerr=yerr, linestyle='',capsize=3, ecolor=colours[idx], label='')
            ax = mean.plot(title=metric + ' vs Congestion', label='') # korzystamy z ostatniego mean df zeby podpisac wykres
            ax.set(xlabel="NSta", ylabel="Mean Per STA " + metric)

            nsta = np.array(nsta)
            nsta = nsta.astype(int)
            indices = np.argsort(nsta)

            sorted_array = [meanArr[indices[j]] for j in range(len(meanArr))]
            nsta.sort()
            #if idx == 0 else ""
            ax.plot(nsta, sorted_array, self.colours[idx], label=str(p[0])+ 'sta/slot') #kropeczki chociaż rysować :)
            ax.legend()

        plt.xlim(self.lim)

        #plt.show(ax)
        fileName = metric + 'Stack' + '.png'
        plt.savefig(self.basePath + fileName ,format='png')
        plt.clf()
        #plt.savefig('N_STA_2Mhz_MCS8.svg',format='svg')

    def makePlotStack(self):
        for met in self.metricToShow:
            self.makePlot(self.subPaths, met)