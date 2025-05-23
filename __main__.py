#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""
Data processing and analysis

The outputs of this analysis were included in SUM D1.1

It requires the raw data from a SumSurvey. They are not publicly available.

@author: panosgtzouras
National Technical University of Athens
Research project: SUM
"""

# %% Import the SumSurveyTools package

root_dir = "/Users/panosgtzouras/Desktop/datasets/csv/SUMsurveyData" # The path with raw data

import SumSurveysTools

from SumSurveysTools.sumSurveyRenameSelect import callData

import os
import pandas as pd
from sumSurveyRenameSelect import callData, missCols, excludeCity
from sumSurveyReplacer import rePlacer, newAssessDF, genRandomTime, fill_na_empirical, sociodummies
from sumAssessAnalysis import (dstatsAssess, heatmapTimeSafe2,
                               plotModalSplit3, heatmapModeTime2, heatmapModePurp,
                               heatmapPeakOff, corrTable, visualizeCorr, DistRtable, visualizeCompare, kolmoTable, satisfyHist)
from sumSurveyFixKrakow import fixKra
from sumSurveyDiariesProc import createDiariesDf
# from sumSurveyDiariesProc import addTripDist

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
# %%
# Step 1. set of Living Labs - Cities
cIE = ['Athens', 'Munich', 'Rotterdam', 'Geneva' , 'Larnaca', 'Krakow', 'Fredrikstad', 'Coimbra', 'Jerusalem'] 

# sets of selected variables
sele1 = ['nonpeakCar', 'nonpeakTaxi', 'nonpeakPT', 'nonpeakMoto', 'nonpeakBike', 'nonpeakWalk',
            'peakCar', 'peakTaxi', 'peakPT', 'peakMoto', 'peakBike', 'peakWalk'] 
sele2 = ['afford', 'satisfy']
sele3 = ['psafeCar', 'psafeTaxi', 'psafePT', 'psafeBike','psafeMoto', 'psafeWalk']
sele4 = ['perSafeCar', 'perSafeTaxi', 'perSafePT', 'perSafeBike','perSafeMoto', 'perSafeWalk']    
sele5 = ['reliable']
sele6 = ['waitBus', 'waitTrain', 'walkBus', 'walkTrain']
# sele7 = ['accept', 'satisfy']
sele = sele1 + sele2 + sele3 + sele4 + sele5 + sele6
# sele = sele + sele7
# %%
# Step 2. set of trip attributes
attr = [
        'orig1','dest1','mode1', 'time1', 'purp1', 
        'orig2','dest2','mode2', 'time2', 'purp2', 
        'orig3','dest3','mode3', 'time3', 'purp3',
        'orig4','dest4','mode4', 'time4', 'purp4', 
        'orig5','dest5','mode5', 'time5', 'purp5'] # origin and destination dimmension is not yet considered

# C. set of Transport Modes
modes = ['car', 'bus', 'walk', 'train', 'motorcycle', 'taxi', 'bicycle', 'micromobility',
         'car sharing', 'ride hailing', 'escooter', 'ferry'] 

char = ['gender', 'age', 'educ', 'employ', 'income']

# D. set of time periods in which the data are collected
w = "finalBefore" # Before the implementation of measures
# %% Step 3. Creation of the Perception Assessment Dataframe
col = ['pid', 'city'] + sele
assess = pd.DataFrame(columns = col)
col2 = ['pid', 'city'] + char
socio = pd.DataFrame(columns = col2)

for c in cIE:
    # Call the data and rename the target columns; only variables included in the matching file
    df = callData(c, when = w)[0]
    # if any column is missing, add it with nans
    df = missCols(df, sele + char)
    # create a general dataframe with all the cities
    assess = pd.concat([assess, df[col]],ignore_index=True)
    socio  = pd.concat([socio, df[col2]],ignore_index=True)


for s in sele: assess = rePlacer(assess, s) # replace the values based on the mappings
assess.dtypes # check the data types, no objects or strings

for c in char: socio = rePlacer(socio, c)

for c in char:
    socio = fill_na_empirical(socio, group_col="city", target_col=c)
socio = sociodummies(socio)

# dstats = dstatsAssess(assess, 'figuresTables/7_descriptive_stats.xlsx') # estimate descriptive statistics

assessDF = newAssessDF(assess) # this creates a new dataframe with levels, integer numbers instead of floats

assess.to_csv(os.path.join(root_dir, 'finalDatasets/"SumSurveyAssessV5.csv'), index = False) # all variables are expressed in levels
# dstats = dstatsAssess(assessDF, 'figuresTables/8_descriptive_stats_newDF.xlsx')
# %% Step 4: Creation of the Diaries Dataframe
col3 = ['pid', 'city'] + attr
diaries = pd.DataFrame(columns = col3)
for c in cIE:
    # same process as in assessment dataframe
    df = callData(c, when = w)[0]
    df = missCols(df, attr)
    diaries = pd.concat([diaries, df[col3]],ignore_index=True)

diaries = createDiariesDf(diaries) # now write all trips in row, each trip is one row
# so diaries now is a set of trips
diaries = fixKra(diaries, w, root_dir) # match the file from Krakow, it has a different format
diaries = rePlacer(diaries, 'mode') # replace the transport modes based on the mappings
diaries = rePlacer(diaries, 'purp') # replace the trip purposes based on the mappings
diaries['time'] =  diaries['time'].apply(genRandomTime) # generate travel times and other

# %% Step 5: Paper32 - SumSurvey first analyis

# assessDF = excludeCity(assessDF, cIE, 'Geneva')[0] # the paper does not consider percpetion assessment data from Geneva
# diaries = excludeCity(diaries, cIE, 'Geneva')[0] # the paper does not consider diaries from Geneva. They are all commuters!
# cIE = excludeCity(assessDF, cIE, 'Geneva')[1] # exclude geneva from the cities list
# corr = corrTable(assessDF, sele, 'figuresTables/9_correlogram.xlsx', 0.05) # estimate a table with correlations
# print(corr.dtypes)
# visualizeCorr(corr) # only statistical significant correlations are shown, kendall correlation test is performed
# the default level of significance in 95%
# kolmostats = kolmoTable(assessDF, sele, "figuresTables/10_kolmogorov_stats_v1.xlsx") # check for similar or not distributions
# this examination is per city and for all the variables.
# distribution_table = DistRtable(kolmostats) # this table indicates the varibles with similar distribution per city

for c in cIE: plotModalSplit3(diaries, c) # the typical modal split pie, each time fix the angle to have nice arrows.
    
visualizeCompare(diaries, assessDF, sele, modes) # this divides the sample to transport mode users and no users
# it compares the mean values, it also test its significance based on Mann-Whittney test, 95% confidence interaval is used

# 99. Extra extra heatmpas
valx = [1, 2, 3, 4, 5, 6, 7] # time level is the set
repx = ["0-15", "15-30", "30-45", "45-60", "60-75", "75-90", ">90"] # time intevals in the set

# Plots for D1.2
# for c in cIE: heatmapPeakOff(assessDF, c, valx, repx) # peak vs nonpeak per transport mode
# for c in cIE: heatmapTimeSafe2(assessDF, c, valx, repx) # peak vs psafe per transport mode
for c in cIE: heatmapModeTime2(diaries, c) # mode vs time distribution
for c in cIE: heatmapModePurp(diaries, c) # mode vs trip purpose distribution

# socio.to_csv(os.path.join(root_dir, "SumSurveySocioV2.csv"), index = False)
# assessDF.to_csv(os.path.join(root_dir, "SumSurveyAssessV2.csv"), index = False)
