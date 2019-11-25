#!/usr/bin/python
import os
import copy
import subprocess
import errno
import re

class SimLauncher:

    def __init__(self,dp, resultsDir, rawObject, BI,  distanceFromAP, payloadSize, seed):
        self.directoryPath = dp
        self.cmd_changable['TrafficPath'] = self.directoryPath + 'OptimalRawGroup/traffic/'
        self.cmd_changable['RAWConfigPath'] = self.directoryPath + 'OptimalRawGroup/'
        self.cmd_changable['NSSFile'] = resultsDir
        self.cmd_const['rho'] = distanceFromAP
        self.cmd_const['payloadSize'] = payloadSize
        self.raws = rawObject 
        self.n = seed
        self.beaconIntervals = BI    

    cmd_const = {}
    cmd_changable = {}

    cmd_const['DataMode'] = 'MCS2_8'
    cmd_const['simulationTime'] = '60'
    cmd_const['TrafficType'] = 'udp'

    cmd_changable['seed'] = '1'
    cmd_changable['Nsta'] = '10'
    cmd_changable['RAWConfigFile'] = './OptimalRawGroup/'

    cmd_changable['pageSliceCount'] = '1'
    cmd_changable['pageSliceLen'] = '0'
    cmd_changable['beaconinterval'] = ''

    cmdsToWrite = ''

    def genCmds(self, bi):
        self.cmd_changable['beaconinterval'] = bi
        cmd_command = './waf --run "'
        cmd_command += 'test'
            
        for i in self.cmd_const.keys():
            cmd_command += ' --' + str(i) + '=' + self.cmd_const[i]        
        waf_commands = []
        all_waf = ''     
        y = 0
        for s in range(1, self.n + 1):
            self.cmd_changable['seed'] = self.n        
            for i in self.raws.keys(): # looping over contention-keys            
                for j in self.raws[i].keys(): # looping over nSta 
                    if self.raws[i][j] is not None:                     
                        waf_commands.append(copy.deepcopy(cmd_command))
                        nSta = str(j) 
                        rGroups = str(self.raws[i][j][0])
                        rSlots = str(self.raws[i][j][1])                    
                        simFolder = self.cmd_changable['NSSFile'] + nSta + '/'                        
                        if not os.path.exists(os.path.dirname(simFolder)):
                            try:
                                os.makedirs(os.path.dirname(simFolder))
                            except OSError as exc:
                                if exc.errno != errno.EEXIST:
                                    raise                                
                        rawFolder = 'c' + i + '/'
                        pathToRaw = self.cmd_changable['RAWConfigPath'] + rawFolder
                        pathToRaw +=  'RawConfig-' + '-' + nSta + '-' + rGroups + '-' + rSlots + '-'
                        pathToRaw += self.cmd_changable['beaconinterval'] + '-' + self.cmd_changable['pageSliceCount'] + \
                             '-' + self.cmd_changable['pageSliceLen'] + '.txt'                 
                        tmp = self.cmd_changable['TrafficPath'] + nSta + 'sta_sim' + '.txt'                                
                        file = nSta + 'sta_sim' + 'G_' + rGroups + '_S_' + rSlots + '_seed_' + str(s)
                        additionalSimInfo = 'BI_' + self.cmd_changable['beaconinterval'] + 'Rho_' + \
                             str(self.cmd_const['rho']) + 'Ps_' + str(self.cmd_const['payloadSize'])
                        waf_commands[y] += ' --NSSFile=' + simFolder + additionalSimInfo + file 
                        waf_commands[y] += ' --seed=' + str(s)
                        waf_commands[y] += ' --RAWConfigFile=' + pathToRaw
                        waf_commands[y] += ' --TrafficPath=' + tmp + ' "'
                                
                        all_waf += waf_commands[y] + '\n'
                        y += 1                  
        self.cmdsToWrite += all_waf

    def writeCmdsToFile(self, commandFile = "waf-commands-aaa.txt"):
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

        while (True):  # Iterowanie po komendach z pliku
            aCommand = AutoWaf.readline()
            if (not aCommand):  # Jesli dojdziemy do konca pliku
                break
            wafCommand = aCommand.split("\n")
            commandLists.append(wafCommand[0])
             # Wykonaj komende
            print("..Wchodze do IEEE-802.11ah-ns-3/ ")
            os.chdir(self.directoryPath)
            print("Wykonuje komende !")
            os.system(wafCommand[0])
            print("Udalo sie przeprowadzic symulacje ...")
