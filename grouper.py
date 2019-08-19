#!/usr/bin/python

import itertools
import math
import numpy as np

def divisorGenerator(n):
    large_divisors = []
    for i in range(1, int(math.sqrt(n) + 1)):
        if n % i == 0:
            yield i
            if i*i != n:
                large_divisors.append(n / i)
    for divisor in reversed(large_divisors):
        yield divisor

# TODO Zrob to ladnie funkcyjnie, in place :
# condition = np.mod(possiblePairs, 16)==2
# np.extract(condition, possiblePairs)

def rawFilter(n, contention):
    x = list(divisorGenerator(n))
    y = [p for p in itertools.product(x, repeat=2)]
    possiblePairs = np.array(y)

    # roznice miedzy elementami :
    diffs = np.diff(possiblePairs)

    # indexy gdzie druga wartosc possiblePairs jest wieksza od pierwszej :
    diff_pos_id = np.where(diffs >= 0)[0]

    possiblePairs = possiblePairs[diff_pos_id]
    #print(possiblePairs)

    wybrani = []
    for  j in range (0, possiblePairs.shape[0]):
        multi = possiblePairs[j][0]*possiblePairs[j][1]
        #print(possiblePairs[j], multi, 16 // multi )
        if((n / multi) == contention):
            #print(n // multi)
            wybrani.append(possiblePairs[j])
    wybrani2 = np.array(wybrani)
    # print(wybrani2)
    # indexy najmniejszych roznic miedzy elementami :
    # tylko jesli jest niepusty :
    
    if wybrani2.size > 0:
        idx = np.argmin(np.diff(wybrani2))
        #print(contention, wybrani2[idx])
        a = wybrani2[idx]
        return [int(a[1]), int(a[0])]

def rawDictGen(nsta, maxSta, maxCont):
    rawDict = {}
    
    # tak na prawde to znaczy ILE STACJI RYWALIZUJE W SLOCIE
    contentions = range(4, maxCont+1) 
    numbers = range(nsta, maxSta + nsta, nsta)

    for c in contentions:
        cont = str(c)
        rawDict[cont] = {}
        for n in numbers:
            nSTA = str(n)
            rawDict[cont][nSTA] = rawFilter(n, c)

    return rawDict

# example :
# raws = rawDictGen(16, 160, 4)
# print(raws)

# a = '/home/soczysty7/Mgr_19/IEEE-802.11ah-ns-3/'
# b = "/home/soczysty7/Mgr_2019/8LipcaClone/IEEE-802.11ah-ns-3/"
# c = 'OptimalRawGroup/traffic/5sta_sim.txt'
# print((a+c)[-12:-11])
# #print(len(a+c))
# print(len(a+c))

# c = 'OptimalRawGroup/traffic/50sta_sim.txt'
# print((a+c)[-13:-11])
# #print(len(a+c))
# print(len(a+c))

# c = 'OptimalRawGroup/traffic/540sta_sim.txt'
# print((a+c)[-14:-11])
# #print(len(a+c))
# print(len(a+c))

# c = 'OptimalRawGroup/traffic/5440sta_sim.txt'
# print((a+c)[-15:-11])
# #print(len(a+c))
# print(len(a+c))

