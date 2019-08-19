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

    def transformFolders(self):
    # 1 Pogrupuj symulacje wg seedów w foldery :

    # for subdir, dirs, files in os.walk(wyniczkiDir):
    #     for file in files:
    #         print(os.path.join(subdir, file))
    #         print(subdir)

        for dirs in os.listdir(self.wyniczkiDir):
            # print(dirs)
            path = self.wyniczkiDir + dirs 
            # print(path)
        
            pat = r'(\d+)sta_simG_(\d+_S_\d+).*'
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

    def analyzeToCsv(self):
    # 2 Skopiuj analyzebatch.pl do wyniczkiDir, skopiuj analyzedata.sh do kazdego folderu np do 32/32  
 
        scriptsDir = '/home/soczysty7/Mgr_19/magister_ludi'

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
                os.system('chmod +x ' + batchScript)  # nie wiedziec czemu to dziala, a os.chmod() nie
                os.system('chmod +x ' + '../analyzebatch.pl')
                command = batchScript + ' > ./' + b + '.csv'
                command = '/bin/bash -c "' + command + '"'
                os.system(command)
            