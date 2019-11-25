#!/usr/bin/python
import os
import re
from shutil import copyfile
from collections import defaultdict

from tempfile import mkstemp
from shutil import move
from os import fdopen, remove

def replace(file_path, pattern, subst):
    #Create temp file
    fh, abs_path = mkstemp()
    with fdopen(fh,'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    #Remove original file
    remove(file_path)
    #Move new file
    move(abs_path, file_path)

class CsvMaker:

    def __init__(self,dp):
        self.wyniczkiDir = dp

    dirStructures = {}

    def transformFolders(self):
    # 1 Pogrupuj symulacje wg seedów w foldery :

        for dirs in os.listdir(self.wyniczkiDir):
            path = self.wyniczkiDir + dirs        
            pat = r'BI_102400Rho_50Ps_1500(\d+)sta_simG_(\d+_S_\d+).*'
            dict_date = defaultdict(lambda : defaultdict(list))
            for fil in os.listdir(path):
                if os.path.isfile(os.path.join(path, fil)):
                    date, animal = re.match(pat, fil).groups()
                    dict_date[date][animal].append(fil)
                
                
            for date in dict_date:
                for animal in dict_date[date]:
                   try:
                       os.makedirs(os.path.join(path, date, animal))
                   except os.error:
                       pass
                   for fil in dict_date[date][animal]:
                       copyfile(os.path.join(path, fil), os.path.join(path, date, animal, fil))
    
    def transformNestedTree(self):
        for dirs in os.listdir(self.wyniczkiDir):
            path = self.wyniczkiDir + dirs
            regex = r'BI_(\d{5,6})Rho_(25|75)Ps_(1024|1500)(\d+)sta_simG_(\d+_S_\d+).*'
            dirStructure = defaultdict(lambda : defaultdict(lambda : defaultdict(list)))
            for nss in os.listdir(path):
                if os.path.isfile(os.path.join(path, nss)):
                    BI, Rho, PS, nSta, rawConf = re.match(regex, nss).groups()
                    psRhoConf = 'Rho_' + Rho + '_Ps_' + PS
                    beaconConf = 'BI_' + BI
                    dirStructure[psRhoConf][beaconConf][rawConf].append(nss)
            self.dirStructures[nSta] = dirStructure
            for psRhoConfig in dirStructure:
                for beaconInterval in dirStructure[psRhoConfig]:
                    for rawConfig in dirStructure[psRhoConfig][beaconInterval]:
                        try:
                            os.makedirs(os.path.join(path, psRhoConfig, beaconInterval, rawConfig))
                        except os.error:
                            pass
                        for filename in dirStructure[psRhoConfig][beaconInterval][rawConfig]:
                            copyfile(os.path.join(path, filename), os.path.join(path, psRhoConfig, beaconInterval, rawConfig, filename))

    def analyzeNestedTree(self, scriptsDir):
        for nStaDict in self.dirStructures:
            path = os.path.join(self.wyniczkiDir, nStaDict)
            for psRhoConfig in self.dirStructures[nStaDict]:
                copyfile((scriptsDir + '/analyzebatch.pl'), os.path.join(path, psRhoConfig, 'analyzebatch.pl'))
                for beaconInterval in self.dirStructures[nStaDict][psRhoConfig]:
                    for rawConfig in self.dirStructures[nStaDict][psRhoConfig][beaconInterval]:
                        batchScript = os.path.join(path, psRhoConfig, beaconInterval, rawConfig + 'analyze.sh')
                        copyfile((scriptsDir + '/analyzedata.sh'), batchScript)
                        replace(batchScript, "batchNameHere", rawConfig)
                        os.chdir(os.path.join(path, psRhoConfig, beaconInterval))
                        os.system('chmod +x ' + batchScript)
                        os.system('chmod +x ' + '../analyzebatch.pl')
                        command = batchScript + ' > ./' + rawConfig + '.csv'
                        command = '/bin/bash -c "' + command + '"'
                        os.system(command)

    def getDirStructures(self):
        return self.dirStructures

    def analyzeToCsv(self, scriptsDir):
    # 2 Skopiuj analyzebatch.pl do wyniczkiDir, skopiuj analyzedata.sh do kazdego folderu np do 32/32  

        for dirs in os.listdir(self.wyniczkiDir):
        
            path = self.wyniczkiDir + '/' + dirs + '/' + dirs 
            batches = os.listdir(path)
            copyfile((scriptsDir + '/analyzebatch.pl'), (self.wyniczkiDir + '/' + dirs + '/analyzebatch.pl'))
                
        # 3 wykonaj analizy do csv :
            
            for b in batches:
                print('[DEBUG]  :  ',  b)
                batchScript = path + '/' + b + 'analyze.sh'
                copyfile((scriptsDir + '/analyzedata.sh'), batchScript)
                replace(batchScript, "batchNameHere", b)
                os.chdir(path)
                os.system('chmod +x ' + batchScript)
                os.system('chmod +x ' + '../analyzebatch.pl')
                command = batchScript + ' > ./' + b + '.csv'
                command = '/bin/bash -c "' + command + '"'
                os.system(command)
            