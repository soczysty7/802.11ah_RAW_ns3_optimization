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

    colours=['r','g','b','k','m']
    metricToShow = ['Latency', 'PacketLoss', 'GoodputKbit', 'EnergyRxIdle', 'EnergyTx']

    def makePlot(self, pathList, metric):
        for idx, p in enumerate(self.subPaths):
            path = self.basePath + p    
            frames = []
            for filename in os.listdir(path):
                if not filename.endswith('csv'):
                    continue
                df = pd.read_csv(os.path.join(path, filename), delimiter=';',usecols=[metric,'BeaconInterval'])
                if not df.empty:
                    frames.append(df)
            fr={}
            for j in range(0, len(frames)):
                i = frames[j]['BeaconInterval'][0]
                print('BI:', i)
                fr[i]=frames[j]
            meanArr = []
            beaconInts = []
            for n in fr.keys():
                fr[n][metric]=fr[n][metric].str.split(",")
                for i in range(0, len(fr[n][metric])):
                    for j in range(0, len(fr[n][metric][i])):
                        fr[n][metric][i][j]=float(fr[n][metric][i][j])
                    fr[n][metric][i]=np.mean(fr[n][metric][i])
                fr[n]=fr[n].astype(float)
                df_nice = fr[n].groupby('BeaconInterval')[metric]
                mean = df_nice.mean()
                print('MEAN', mean)
                beaconInts.append(mean.index[0])
                std = df_nice.std()
                meanArr.append(mean.data[0])
                alpha=0.05
                n = df_nice.count()
                yerr = std / np.sqrt(n) * st.t.ppf(1-alpha/2, n - 1)
            ax = mean.plot(title=metric + ' vs Congestion', label='')
            ax.set(xlabel="BeaconInterval", ylabel="Mean Per STA " + metric)
            beaconInts = np.array(beaconInts)
            beaconInts = beaconInts.astype(int)
            indices = np.argsort(beaconInts)
            sorted_array = [meanArr[indices[j]] for j in range(len(meanArr))]
            beaconInts.sort()
            match1 = re.search(r'2_S_(\d+)', p)
            legendOzn = match1[1] + ' slots'        
            ax.plot(beaconInts, sorted_array, self.colours[idx], marker='o', label=legendOzn)
            ax.legend()

        plt.show(ax)
        # fileName = metric + 'Stack' + '.svg'
        # plt.savefig(self.basePath + fileName ,format='svg')
        # plt.clf()

    def makePlotStack(self):
        for met in self.metricToShow:
            self.makePlot(self.subPaths, met)
