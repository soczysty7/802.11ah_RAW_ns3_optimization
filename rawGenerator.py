#!/usr/bin/python
import os
import copy
import subprocess
import errno

class RawMaker:

    def __init__(self,dp, rawObject, BI):
        self.directoryPath = dp
        self.beaconIntervals = BI
        self.arg_zmienne['RAWConfigPath'] = self.directoryPath + 'OptimalRawGroup/'
        self.raws = rawObject 

        # na razie wszystkie arg sa stale a zmienne generowane z rawObj :)

    
    arg_stale = {}
    arg_zmienne = {}

    # Argumenty stale :

    arg_stale['pageSliceCount'] = '1'
    arg_stale['pageSliceLen'] = '0'

    # Argumenty zmienne default:

    arg_zmienne['NRawSta'] = ''
    arg_zmienne['NGroup'] = ''
    arg_zmienne['NumSlot'] = ''
    arg_zmienne['beaconinterval'] = ''
    #arg_zmienne['RAWConfigPath'] = directoryPath + 'OptimalRawGroup/' Patrz wyzej-init

    cmdsToWrite = ''

    def genCmds(self, bi):
        self.arg_zmienne['beaconinterval'] = bi
        cmd_command = './waf --run "'
        cmd_command += 'RAW-generate'

        for i in self.arg_stale.keys():
            cmd_command += ' --' + str(i) + '=' + self.arg_stale[i]

        waf_commands = []  # lista komend
        all_waf = '' # string komend ; do wpisania do pliku

        y = 0

        # Konstrukcja komend :

        for i in self.raws.keys(): # looping over contention-keys

            for j in self.raws[i].keys(): # looping over nSta 
                if self.raws[i][j] is not None: 

                
                    rawFolder = 'c' + i + '/'
                    pathToRaw = self.arg_zmienne['RAWConfigPath'] + rawFolder
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
                    pathToRaw += self.arg_zmienne['beaconinterval'] + '-' + self.arg_stale['pageSliceCount'] + '-' + self.arg_stale['pageSliceLen'] + '.txt'

                    self.arg_zmienne['NRawSta'] = nSta
                    self.arg_zmienne['NGroup'] = rGroups
                    self.arg_zmienne['NumSlot'] = rSlots

            # Single run of RAW Generator is :

            # ./waf --run "RAW-generate --NRawSta=$NumSta --NGroup=$NRawGroups --NumSlot=$NumSlot 
            # --RAWConfigPath=$RAWConfigPath --beaconinterval=$beaconinterval --pageSliceCount=$pageSliceCount 
            # --pageSliceLen=$pageSliceLen"

                    waf_commands[y] += ' --NRawSta=' + self.arg_zmienne['NRawSta']
                    waf_commands[y] += ' --NGroup=' + self.arg_zmienne['NGroup']
                    waf_commands[y] += ' --NumSlot=' + self.arg_zmienne['NumSlot']
                    waf_commands[y] += ' --RAWConfigPath=' + pathToRaw
                    waf_commands[y] += ' --beaconinterval=' + self.arg_zmienne['beaconinterval']
                    waf_commands[y] += ' --pageSliceCount=' + self.arg_stale['pageSliceCount'] 
                    waf_commands[y] += ' --pageSliceLen=' + self.arg_stale['pageSliceLen'] + '"'

                    all_waf += waf_commands[y] + '\n'
                    y += 1

        # ----------------------------
        self.cmdsToWrite += all_waf
        #return all_waf

    def writeCmdsToFile(self):
        # Pisanie komend do pliku:

        for bi in self.beaconIntervals:
            self.genCmds(bi)
        AutoWaf = open("waf-commands-rawGenerate.txt", "w")
        print("Wpisuje wygenerowane komendy do pliku...")
        AutoWaf.writelines(self.cmdsToWrite)
        AutoWaf.close()

    def generateRawConfigs(self):

        AutoWaf = open("waf-commands-rawGenerate.txt", "r")
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
            print("Udalo sie wygenerowac RAW ...")