#!/usr/bin/python
import os
import re
from shutil import copyfile
from collections import defaultdict

from tempfile import mkstemp
from shutil import move
from os import fdopen, remove

import grouper as gr

def regGroupMatcher(nsta, ngr, nsl, test_str):
    # tworzymy regexa i patrzymy ktora .csv maczuje,
    regex = '(' + str(nsta) + ')/(' + str(ngr) + ')_S_(' + str(nsl) + ')'
    matches = [re.findall(regex,l) for l in test_str]
    indexes = [i for i,v in enumerate(matches) if v]
    return test_str[indexes[0]]

class PreparePlot:

    def __init__(self,resultsDir, plotDir, rawObject):
        self.wyniczkiDir = resultsDir
        self.csvToGraphDir = plotDir
        self.raws = rawObject
        self.csvList()

    csvKi = []

    def csvList(self):

        for subdir, dirs, files in os.walk(self.wyniczkiDir):
            for file in files:
                if not file.endswith('csv'):
                    continue
                csvPath = os.path.join(subdir, file)
                self.csvKi.append(csvPath)
    
    def prepareEnergyCampainDirs(self, dirStructures):
        print(dirStructures.keys())
        for nStaDict in dirStructures:
            path = os.path.join(self.wyniczkiDir, nStaDict)
            for psRhoConfig in dirStructures[nStaDict]:
                for beaconInterval in dirStructures[nStaDict][psRhoConfig]:
                    for rawConfig in dirStructures[nStaDict][psRhoConfig][beaconInterval]:
                        toCreate = os.path.join(self.csvToGraphDir, nStaDict, rawConfig)
                        if not os.path.exists(toCreate):
                            try:
                                os.makedirs(toCreate)
                            except OSError as exc:  # Guard against race condition
                                if exc.errno != errno.EEXIST:
                                    raise
                        oldCSVpath = os.path.join(path, psRhoConfig, beaconInterval, rawConfig + '.csv')
                        newCSVpath = os.path.join(toCreate, beaconInterval + '_' + os.path.basename(oldCSVpath))
                        copyfile(oldCSVpath, newCSVpath)                        

    def prepareFolders(self):
        for i in self.raws.keys(): # looping over contention-keys
            for j in self.raws[i].keys(): # looping over nSta 
                if self.raws[i][j] is not None: 
                    nGroups = self.raws[i][j][0]
                    nSlo = self.raws[i][j][1]
                    # stworz folder ic
                    contFolder = '/' + i + 'c/'
                    toCreate = self.csvToGraphDir + contFolder
                    if not os.path.exists(os.path.dirname(toCreate)):
                        try:
                            os.makedirs(os.path.dirname(toCreate))
                        except OSError as exc:  # Guard against race condition
                            if exc.errno != errno.EEXIST:
                                raise

                    oldCSVpath = regGroupMatcher(j,nGroups,nSlo,self.csvKi)
                    newCSVpath = toCreate + 'nsta' + str(j) + '_' + os.path.basename(oldCSVpath)
                    copyfile(oldCSVpath, newCSVpath)
