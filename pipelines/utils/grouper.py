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

def rawFilter(n, contention):
    x = list(divisorGenerator(n))
    y = [p for p in itertools.product(x, repeat=2)]
    possiblePairs = np.array(y)
    # roznice miedzy elementami :
    diffs = np.diff(possiblePairs)
    # indexy gdzie druga wartosc possiblePairs jest wieksza od pierwszej :
    diff_pos_id = np.where(diffs >= 0)[0]
    possiblePairs = possiblePairs[diff_pos_id]
    wybrani = []
    for  j in range (0, possiblePairs.shape[0]):
        multi = possiblePairs[j][0]*possiblePairs[j][1]
        if((n / multi) == contention):
            wybrani.append(possiblePairs[j])
    wybrani2 = np.array(wybrani)
    # indexy najmniejszych roznic miedzy elementami :
    # tylko jesli jest niepusty :    
    if wybrani2.size > 0:
        idx = np.argmin(np.diff(wybrani2))
        a = wybrani2[idx]
        return [int(a[1]), int(a[0])]

def rawDictGen(numbers, maxCont):
    rawDict = {}
    for c in maxCont:
        cont = str(c)
        rawDict[cont] = {}
        for n in numbers:
            nSTA = str(n)
            rawDict[cont][nSTA] = rawFilter(n, c)
    return rawDict

def staticDictGen(numbers, gsBit, maxCont, staticNumber):
    # gsBit : true zmieniamy liczba GRUP a slot ustawiamy na staticNumber (stala)
    #         false: zmieniamy liczba SLOTOW a grup ustawiamy na staticNumber (stala)
    # generuje rawObj {N (grup, slotow) : nSTA: [nGR, nSLOT]
    rawDict = {}
    for c in maxCont:
        cont = str(c)
        rawDict[cont] = {}
        for n in numbers:
            nSTA = str(n)
            if c < n:
                tmp = [c,staticNumber] if gsBit else [staticNumber,c] 
                rawDict[cont][nSTA] = tmp
    return rawDict   

"""
# Example :

contentions = [1, 2, 5]
numberOfStations = [250, 1000, 2000]

# try grouppings for 3 cases : 

# 1 static number of RAW slots :
# pogrupuj 250, 1000, 2000 stacji w : 1, 2, 5 grup po 10 slotow kazda :

# raws = staticDictGen(numberOfStations, True, contentions, 10)

# 2 static number of RAW groups :
# pogrupuj 250, 1000, 2000 stacji w : 10 grup po 1, 2, 5 slotow kazda :

# raws = staticDictGen(numberOfStations, False, contentions, 10)

# 3 only given number of contentions per RAW slot :
# pogrupuj 250, 1000, 2000 stacji w we wszystkie mozliwe kombinacje,
# tak ze na jeden slot przypada 1, 2 lub 5 stacji :

raws = rawDictGen(numberOfStations, contentions)
print(raws)
"""
