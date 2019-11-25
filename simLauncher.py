#!/usr/bin/python
import os
import copy
import subprocess
import errno
import re

class SimLauncher:
    """
Przykladowa symulacja ktora my chcemy puszczac :

./waf --run "test --TrafficType=udp --DataMode=MCS2_8 --simulationTime=60 
--rho=50 --payloadSize=1500 --NSSFile=../wyniczki/NSTA/plik symulki
--seed=1 --RAWConfigFile=./OptimalRawGroup/c1/RawConfig--16-4-4-102400-0-1.txt
--TrafficPath=/home/soczysty7/IEEE-802.11ah-ns-3/OptimalRawGroup/traffic/16sta_sim.txt"

na razie wszystkie arg sa stale a zmienne generowane z rawObj :

Raws to slownik zawierajacy wszystkie konfiguracje do przetestowania na 
ktorych bazowal rawGenerator robiac pliki rawconfigow :
    """

    def __init__(self,dp, resultsDir, rawObject, BI,  distanceFromAP, payloadSize, seed):
        self.directoryPath = dp
        self.arg_zmienne['TrafficPath'] = self.directoryPath + 'OptimalRawGroup/traffic/'
        self.arg_zmienne['RAWConfigPath'] = self.directoryPath + 'OptimalRawGroup/'
        self.arg_zmienne['NSSFile'] = resultsDir
        self.arg_stale['rho'] = distanceFromAP
        self.arg_stale['payloadSize'] = payloadSize
        self.raws = rawObject 
        self.n = seed
        self.beaconIntervals = BI    
        #RunSimulations()


    arg_stale = {}
    arg_zmienne = {}

    # Argumenty stale :

    arg_stale['DataMode'] = 'MCS2_8'
    # arg_stale['payloadSize'] = '100'
    arg_stale['simulationTime'] = '60'
    # arg_stale['rho'] = '50'
    arg_stale['TrafficType'] = 'udp'

    # Argumenty zmienne default:

    arg_zmienne['seed'] = '1'
    arg_zmienne['Nsta'] = '10'
    arg_zmienne['RAWConfigFile'] = './OptimalRawGroup/'

    # For raw files searching :
    arg_zmienne['pageSliceCount'] = '1'
    arg_zmienne['pageSliceLen'] = '0'
    arg_zmienne['beaconinterval'] = ''

    cmdsToWrite = ''

    def genCmds(self, bi):
        self.arg_zmienne['beaconinterval'] = bi
        cmd_command = './waf --run "'
        cmd_command += 'test'
            
        for i in self.arg_stale.keys():
            cmd_command += ' --' + str(i) + '=' + self.arg_stale[i]
        
        waf_commands = []  # lista komend
        all_waf = '' # string komend ; do wpisania do pliku
        
        y = 0
        
        # Konstrukcja komend :
        
        for s in range(1, self.n + 1):
            self.arg_zmienne['seed'] = self.n
        
            for i in self.raws.keys(): # looping over contention-keys
            
                for j in self.raws[i].keys(): # looping over nSta 
                    if self.raws[i][j] is not None: 
                    
                        waf_commands.append(copy.deepcopy(cmd_command))
                        nSta = str(j) 
                        rGroups = str(self.raws[i][j][0])
                        rSlots = str(self.raws[i][j][1])
                    
                        simFolder = self.arg_zmienne['NSSFile'] + nSta + '/'
                        
                        if not os.path.exists(os.path.dirname(simFolder)):
                            try:
                                os.makedirs(os.path.dirname(simFolder))
                            except OSError as exc:  # Guard against race condition
                                if exc.errno != errno.EEXIST:
                                    raise
                                
                        rawFolder = 'c' + i + '/'
                        pathToRaw = self.arg_zmienne['RAWConfigPath'] + rawFolder
                        pathToRaw +=  'RawConfig-' + '-' + nSta + '-' + rGroups + '-' + rSlots + '-'
                        pathToRaw += self.arg_zmienne['beaconinterval'] + '-' + self.arg_zmienne['pageSliceCount'] + '-' + self.arg_zmienne['pageSliceLen'] + '.txt'
                                
                        tmp = self.arg_zmienne['TrafficPath'] + nSta + 'sta_sim' + '.txt'
                                
                        file = nSta + 'sta_sim' + 'G_' + rGroups + '_S_' + rSlots + '_seed_' + str(s)
                        additionalSimInfo = 'BI_' + self.arg_zmienne['beaconinterval'] + 'Rho_' + str(self.arg_stale['rho']) + 'Ps_' + str(self.arg_stale['payloadSize'])
                        waf_commands[y] += ' --NSSFile=' + simFolder + additionalSimInfo + file 
                        waf_commands[y] += ' --seed=' + str(s)
                        waf_commands[y] += ' --RAWConfigFile=' + pathToRaw
                        waf_commands[y] += ' --TrafficPath=' + tmp + ' "'
                                
                        all_waf += waf_commands[y] + '\n'
                        y += 1                  
        # ----------------------------
        self.cmdsToWrite += all_waf
        #return all_waf


    def writeCmdsToFile(self, commandFile = "waf-commands-aaa.txt"):
        # Pisanie komend do pliku:
        for bi in self.beaconIntervals:
            self.genCmds(bi)
        AutoWaf = open(commandFile, "w")
        print("Wpisuje wygenerowane komendy do pliku...")
        AutoWaf.writelines(self.cmdsToWrite)
        AutoWaf.close()

    def RunSimulations(self, commandFile = "waf-commands-aaa.txt"):

        AutoWaf = open(commandFile, "r")
        commandLists = []  # Create an array to store our waf commands
        os.getcwd()
        print("Wczytuje komendy z przygotowanego pliku ...")

        # Start While :

        while (True):  # Iterowanie po komendach z pliku
            aCommand = AutoWaf.readline()
            if (not aCommand):  # Jesli dojdziemy do konca pliku
                break
            # Wyciagnij z pliku komendy wg \n
            wafCommand = aCommand.split("\n")
            commandLists.append(wafCommand[0])
            print(commandLists)
            # Wyciagnieta komenda :
            print("Komenda: %s" % (wafCommand[0]))
            # Wykonaj komende
            print("..Wchodze do IEEE-802.11ah-ns-3/ ")
            os.chdir(self.directoryPath)
            #subprocess.call(["ls"])
            print("Wykonuje komende !")
            os.system(wafCommand[0])
            print("Udalo sie przeprowadzic symulacje ...")