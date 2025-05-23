#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Functions to transform Krakow Survey data

@author: panosgtzouras
National Technical University of Athens
Research project: SUM
"""

import pandas as pd
import os
from sumSurveyRenameSelect import callData

def kraDiar(df, kradiar):
    
    # root_dir = os.path.dirname(os.path.realpath(__file__))
    
    # print(kradiar)
    
    column_mapping = {
    'Proszę wskazać koniec Pani/Pana podróży:': 'dest',
    
    "Proszę wskazać początek swojej pierwszej podróży (gdzie rozpoczęła Pani/Pan podróż?):": 'orig',
    
    'Jaki środek transportu wybrała/ał Pani/Pan, aby dotrzeć do celu? Proszę wskazać główny środek transportu podczas Pani/Pana podróży.': 'mode',
    'Proszę wskazać motywację (powód) swojej podróży:': 'purp',
    'Proszę wskazać godzinny, w jakich odbywała się Pani/Pana podróż?': 'time'}
    
    
    kradiar = kradiar.rename(columns=column_mapping)
    # print(kradiar)

    ndf = pd.merge(df, kradiar, left_on="GlobalID", right_on = 'ParentGlobalID')
    
    selected_columns = ['pid', 'city', 'orig','dest', 'mode', 'time', 'purp']
    
    ndf = ndf[selected_columns]
    
    return ndf

def fixKra(df, w, path): 
    kra = kraDiar(callData('Krakow', when = w)[0][['pid', 'city', 'GlobalID']], 
              pd.read_csv(os.path.join(path, 'rawDatasets' , 'Krakow', 'diaryDatasetKra.csv'), delimiter=';'))
    df = pd.concat([df, kra],ignore_index=True).dropna(subset=['mode', 'purp', 'time'])
    # df = df.drop(columns = ['dest'])
    return df

