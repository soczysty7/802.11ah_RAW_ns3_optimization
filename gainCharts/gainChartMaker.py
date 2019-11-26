#!/usr/bin/python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as st
import os, re

inputPath = '/home/soczysty7/magister_ludi/gainCharts/inputData/'
outputPath = '/home/soczysty7/magister_ludi/gainCharts/outputGainCharts/'
metrics = ['Latency', 'PacketLoss', 'GoodputKbit', 'EnergyRxIdle', 'EnergyTx']
rawConfigs = ['groups', 'slots']
traffic = ['sat', 'non_sat']
basicEthics = ['good', 'bad']

def populateGainMap():
    gainMap = {}
    for raw in rawConfigs:
        gainMap[raw] = {}
        for m in metrics:
            gainMap[raw][m] = {}
            for state in traffic:
                tmpPath = os.path.join(inputPath, raw, m, state)
                gainMap[raw][m][state] = aggregateCsvToGains(tmpPath, m)
    return gainMap

def aggregateCsvToGains(dirPath, metric):
    frames = {}
    good = []
    bad = []
    for e in basicEthics:
        csvDirPath = os.path.join(dirPath, e)
        for subdir, dirs, files in os.walk(csvDirPath):
            for file in files:
                match = re.search(r'nsta(\d{2,3})', file)
                nSta = match[1]
                df = pd.read_csv(os.path.join(subdir, file), delimiter=';',usecols=metrics)
                countMeansInDataFrame(bad, good, e, df, frames, nSta, metric)
    return calculateGain(bad, good)

def countMeansInDataFrame(b, g, e, dataFrame, frameDict, n, m):
    frameDict[n] = dataFrame
    frameDict[n][m] = frameDict[n][m].str.split(",")
    convertDataFrameToFloatMean(frameDict[n], m)
    magicMean = frameDict[n][m].mean()
    if e is 'good':
        g.append(magicMean.mean())
    else:
        b.append(magicMean.mean())

def convertDataFrameToFloatMean(df, met):
    for i in range(0, len(df[met])):
        for j in range(0, len(df[met][i])):
            df[met][i][j] = float(df[met][i][j])
        df[met][i] = np.mean(df[met][i])

def calculateGain(low, high):
    low = np.mean(low)
    high = np.mean(high)
    gain = ((high - low) / low) * 100
    print(high, low)
    return abs(gain)

def makePlots(gainMap):
    for raw in rawConfigs:
        satMeans = []
        nonSatMeans = []
        for met in metrics:
            for key, value in gainMap[raw][met].items():
                if key is 'sat':
                    satMeans.append(value)
                else:
                    nonSatMeans.append(value)
        satMeans = tuple(satMeans)
        nonSatMeans = tuple(nonSatMeans)
        produceBarChart(satMeans, nonSatMeans, raw)

def produceBarChart(satMeans, nonSatMeans, Raw):
    fig, ax = plt.subplots()
    ind = np.arange(5)    # the x locations for the groups
    width = 0.35          # the width of the bars
    p1 = ax.bar(ind, satMeans, width, bottom=0)
    p2 = ax.bar(ind + width, nonSatMeans, width, bottom=0)
    plt.ylabel('Gain [%]')
    ax.set_xticks(ind + width / 2)
    ax.set_xticklabels(('Latency', 'PacketLoss', 'GoodputKbit', 'EnergyRxIdle', 'EnergyTx'))
    ax.legend((p1[0], p2[0]), ('Saturation', 'Non-saturation'))
    ax.autoscale_view()
    # plt.show()
    chartName = 'summary_' + Raw + '_gains.svg'
    outFile = os.path.join(outputPath, chartName)
    plt.savefig(outFile,format='svg')

gainTestMap = populateGainMap()
makePlots(gainTestMap)