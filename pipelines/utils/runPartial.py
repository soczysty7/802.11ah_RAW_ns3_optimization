#!/usr/bin/python
import os, re

oldCmdFile = '/home/soczysty7/magister_ludi/REMAINING.txt'
newCmdFile = '/home/soczysty7/magister_ludi/REMAINING2.txt'
resultDirToExplore = '/home/soczysty7/Mgr19/Results/nowyArtNonCSB_4_11/500udp_slots_NonSAT/'


def runRemaining(path, commandFile):
    AutoWaf = open(commandFile, "r")
    commandLists = []
    all_waf = ''

    while (True): 
        aCommand = AutoWaf.readline()
        if (not aCommand):
            break
        wafCommand = aCommand.split("\n")

        if isResultNssPresentInPath(path, wafCommand[0]):
            all_waf += wafCommand[0] + '\n'

    commandLists.append(all_waf)
    writeCmdsToFile(newCmdFile, commandLists)
    writeRemainingCommands(oldCmdFile, newCmdFile)

def isResultNssPresentInPath(path, command):
    reg1 = r'--NSSFile=((.)+)\s(--seed)'
    match = re.search(reg1, command)
    fileToCheck = os.path.basename(match[1]) + '.nss'

    for subdir, dirs, files in os.walk(path):
        if fileToCheck in files:
            return True

def writeCmdsToFile(commandFile, remainingCmds):
    AutoWaf = open(commandFile, "w")
    AutoWaf.writelines(remainingCmds)
    AutoWaf.close()

def writeRemainingCommands(old, new):
    with open(old, 'r') as file1:
        with open(new, 'r') as file2:
            diff = set(file1).difference(file2)
    diff.discard('\n')
    with open(new, 'w') as file_out:
        for line in diff:
            file_out.write(line)

runRemaining(resultDirToExplore, oldCmdFile)