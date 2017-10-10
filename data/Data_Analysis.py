# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 10:20:28 2017

@author: etien
"""

import collections
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

LBH = []
with open('C:/Users/etien/Documents/Github/Probabilistic_Language_Change/data/phrase_functions/phrase_functions_LBH.txt') as inputfile:
    for line in inputfile:
        LBH.append(line.strip().split(' '))


EBH = []
with open('C:/Users/etien/Documents/Github/Probabilistic_Language_Change/data/phrase_functions/phrase_functions_EBH.txt') as inputfile:
    for line in inputfile:
        EBH.append(line.strip().split(' '))

########################## EBH
        
setEBH = set()
for item in EBH:
    for abstract in item:
        setEBH.add(abstract)

uniqueFunctionsEBH = sorted(list(setEBH))
zeromatrixEBH = np.zeros((len(EBH), len(setEBH)))

for row,item in enumerate(EBH):
    for function in item:
        column = uniqueFunctionsEBH.index(function)
        zeromatrixEBH[row][column]+=1
        
dfEBH = pd.DataFrame(zeromatrixEBH, columns = uniqueFunctionsEBH)
        
frequenciesEBH = dfEBH.sum(0).to_dict()
for key, value in frequenciesEBH.items():
    frequenciesEBH[key] = value / len(EBH)
    
amountFunctionsEBH = np.asarray(dfEBH.sum(1))
min(amountFunctionsEBH)
max(amountFunctionsEBH)

counter = collections.Counter(amountFunctionsEBH)
print(counter)
plt.hist(amountFunctionsEBH,[1,2,3,4,5,6,7], normed=True)


########################## LBH

setLBH = set()
for item in LBH:
    for abstract in item:
        setLBH.add(abstract)

uniqueFunctionsLBH = sorted(list(setLBH))
zeromatrixLBH = np.zeros((len(LBH), len(setLBH)))

for row,item in enumerate(LBH):
    for function in item:
        column = uniqueFunctionsLBH.index(function)
        zeromatrixLBH[row][column]+=1
        
dfLBH = pd.DataFrame(zeromatrixLBH, columns = uniqueFunctionsLBH)
        
frequenciesLBH = dfLBH.sum(0).to_dict()
for key, value in frequenciesEBH.items():
    frequenciesLBH[key] = value / len(LBH)
    
amountFunctionsLBH = np.asarray(dfLBH.sum(1))
min(amountFunctionsLBH)
max(amountFunctionsLBH)
counter = collections.Counter(amountFunctionsLBH)
print(counter)
plt.hist(amountFunctionsLBH,[1,2,3,4,5,6,7], normed=True)

#SRATISTICS
stats.bartlett(amountFunctionsEBH,amountFunctionsLBH)
stats.mstats.kruskalwallis(amountFunctionsEBH,amountFunctionsLBH)

np.var(amountFunctionsEBH)
np.var(amountFunctionsLBH)
np.mean(amountFunctionsEBH)
np.mean(amountFunctionsLBH)

stats.ttest_ind(amountFunctionsEBH,amountFunctionsLBH)

#Occurences of functions
dfLBHCount = dfLBH.groupby(dfLBH.columns.tolist()).size().reset_index().rename(columns={0:'count'})
dfLBHCount['count'] = dfLBHCount['count']/len(LBH)
dfLBHCount.sort("count", ascending=False)[:5]

dfEBHCount = dfEBH.groupby(dfEBH.columns.tolist()).size().reset_index().rename(columns={0:'count'})
dfEBHCount['count'] = dfEBHCount['count']/len(EBH)
dfEBHCount.sort("count", ascending=False)[:5]








