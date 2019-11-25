#!/usr/bin/python
import os
import copy
import subprocess
import errno

class RawMaker:

    def __init__(self,dp, rawObject, BI):
        self.directoryPath = dp
        self.beaconIntervals = BI
        self.cmd_changable['RAWConfigPath'] = self.directoryPath + 'OptimalRawGroup/'
        self.raws = rawObject 

    cmd_const = {}
    cmd_changable = {}
    cmd_const['pageSliceCount'] = '1'
    cmd_const['pageSliceLen'] = '0'
    cmd_changable['NRawSta'] = ''
    cmd_changable['NGroup'] = ''
    cmd_changable['NumSlot'] = ''
    cmd_changable['beaconinterval'] = ''
    cmdsToWrite = ''

    def genCmds(self, bi):
        self.cmd_changable['beaconinterval'] = bi
        cmd_command = './waf --run "'
        cmd_command += 'RAW-generate'

        for i in self.cmd_const.keys():
            cmd_command += ' --' + str(i) + '=' + self.cmd_const[i]
        waf_commands = []
        all_waf = ''
        y = 0
        for i in self.raws.keys(): # looping over contention-keys
            for j in self.raws[i].keys(): # looping over nSta 
                if self.raws[i][j] is not None:                 
                    rawFolder = 'c' + i + '/'
                    pathToRaw = self.cmd_changable['RAWConfigPath'] + rawFolder
                    if not os.path.exists(os.path.dirname(pathToRaw)):
                        try:
                            os.makedirs(os.path.dirname(pathToRaw))
                        except OSError as exc:  # Guard against race condition
                            if exc.errno != errno.EEXIST:
                                raise
                    waf_commands.append(copy.deepcopy(cmd_command))
                    nSta = str(j) 
                    rGroups = str(self.raws[i][j][0])
                    rSlots = str(self.raws[i][j][1])
                    pathToRaw +=  'RawConfig-' + '-' + nSta + '-' + rGroups + '-' + rSlots + '-'
                    pathToRaw += self.cmd_changable['beaconinterval'] + '-' + \
                        self.cmd_const['pageSliceCount'] + '-' + self.cmd_const['pageSliceLen'] + '.txt'
                    self.cmd_changable['NRawSta'] = nSta
                    self.cmd_changable['NGroup'] = rGroups
                    self.cmd_changable['NumSlot'] = rSlots
                    waf_commands[y] += ' --NRawSta=' + self.cmd_changable['NRawSta']
                    waf_commands[y] += ' --NGroup=' + self.cmd_changable['NGroup']
                    waf_commands[y] += ' --NumSlot=' + self.cmd_changable['NumSlot']
                    waf_commands[y] += ' --RAWConfigPath=' + pathToRaw
                    waf_commands[y] += ' --beaconinterval=' + self.cmd_changable['beaconinterval']
                    waf_commands[y] += ' --pageSliceCount=' + self.cmd_const['pageSliceCount'] 
                    waf_commands[y] += ' --pageSliceLen=' + self.cmd_const['pageSliceLen'] + '"'
                    all_waf += waf_commands[y] + '\n'
                    y += 1
        self.cmdsToWrite += all_waf

    def writeCmdsToFile(self):
        for bi in self.beaconIntervals:
            self.genCmds(bi)
        AutoWaf = open("waf-commands-rawGenerate.txt", "w")
        AutoWaf.writelines(self.cmdsToWrite)
        AutoWaf.close()

    def generateRawConfigs(self):
        AutoWaf = open("waf-commands-rawGenerate.txt", "r")
        commandLists = []  # Create an array to store our waf commands
        os.getcwd()
        print("Wczytuje komendy z przygotowanego pliku ...")
        while (True):  # Iterowanie po komendach z pliku
            aCommand = AutoWaf.readline()
            if (not aCommand):  # Jesli dojdziemy do konca pliku
                break
            # Wyciagnij z pliku komendy wg \n
            wafCommand = aCommand.split("\n")
            commandLists.append(wafCommand[0])
            print("..Wchodze do IEEE-802.11ah-ns-3/ ")
            os.chdir(self.directoryPath)
            print("Wykonuje komende !")
            os.system(wafCommand[0])
            print("Udalo sie wygenerowac RAW config ...")
