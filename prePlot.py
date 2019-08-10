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
    #return matches[indexes[0]][0]
    return test_str[indexes[0]]

class PreparePlot:

    def __init__(self,resultsDir, plotDir, rawObject):
        self.wyniczkiDir = resultsDir
        self.csvToGraphDir = plotDir
        self.raws = rawObject
        self.csvList()

    csvKi = []

# for dirs in os.listdir(self.wyniczkiDir):
#     # print(dirs)
#     path = self.wyniczkiDir + '/' + dirs  + '/' + dirs 
#     print(path)

#     #pat = r'(\d+)sta_simG_(\d+_S_\d+).*'

    def csvList(self):

        for subdir, dirs, files in os.walk(self.wyniczkiDir):
            for file in files:
                if not file.endswith('csv'):
                    continue
                csvPath = os.path.join(subdir, file)
                #print(os.path.join(subdir, file))
                self.csvKi.append(csvPath)
                #date, animal = re.match(pat, fil).groups()
                #print(subdir)

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

                    #skopiuj do niego csv regex = r'(j)/(nGroups)_S_(nSlo)'
                    oldCSVpath = regGroupMatcher(j,nGroups,nSlo,self.csvKi)
                    newCSVpath = toCreate + os.path.basename(oldCSVpath)
                    copyfile(oldCSVpath, newCSVpath)

