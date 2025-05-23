#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
City parameters for data processing

@author: panosgtzouras
National Technical University of Athens
Research project: SUM
"""

import pandas as pd
import os

def droper (df, city):
    if city == 'Rotterdam':
        df = df.drop(0)
        df = df.drop(1)
        df = df.drop(2)
    
    if city == 'Munich':
        df = df.drop(0)
    
    if city == 'Athens':
        df = df.drop(0)
        
    if city == 'Krakow':
        df = df.drop(0)
        
    if city == 'Geneva':
        df = df.drop(0)
    
    if city == 'Larnaca':
        df = df.drop(0)
    
    if city == 'Fredrikstad':
        df = df.drop(0)
    
    if city == 'Coimbra':
        df  = df.drop(0)
    
    df = df.reset_index(drop = True)
    return df


def head(city):
    if city == 'Athens':
        head = 0
    elif city == 'Munich':
        head = 0
    elif city == 'Rotterdam':
        head = 1
    elif city == 'Larnaca':
        head = 0
    elif city == 'Krakow':
        head = 0
    elif city == 'Geneva':
        head = 0
    elif city == 'Fredrikstad':
        head = 0
    elif city == 'Coimbra':
        head = 0
    else: head = 0
    
    return (head)

# delegated
def encode(city):
    if city == 'Athens':
        encode = 'iso-8859-7'
    elif city == 'Munich':
        encode = 'cp1252' 
    elif city == 'Rotterdam':
        encode = 'cp1252' 
    else: encode = 'utf-8' 
    return (encode)

def pidValue(city):
    if city == 'Athens':
        pidValue = 1000
    elif city == 'Munich':
        pidValue = 2000
    elif city == 'Rotterdam':
        pidValue = 3000
    elif city == 'Larnaca':
        pidValue = 4000
    elif city == 'Krakow':
        pidValue = 5000
    elif city == 'Geneva':
        pidValue = 6000
    elif city == 'Fredrikstad':
        pidValue = 7000
    elif city == 'Coimbra':
        pidValue = 8000
    else: pidValue = 0
    return pidValue

def saveCols(df, city, path):
    saveColsPath = os.path.join(path, 'questionsMatch', 'columns' + city + '.csv')
    df = pd.read_csv(os.path.join(path, 'sampleDatasets' ,city, 'surveyDataset.csv'), delimiter=',', 
                         header = head(city))
    cols = pd.DataFrame(df.columns.tolist())
    cols['name2'] = 'NotFound'
    cols = cols.rename(columns = {0: "name1"})
    cols.to_csv(saveColsPath, index = False, encoding = encode(city))