#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Functions that returns the mapping dictionaries

Responses have been collected in more than 9 languages

@author: panosgtzouras
National Technical University of Athens
Research project: SUM
"""

import numpy as np
import pandas as pd
import re
import os

def extract_numbers(text):
    if isinstance(text, str):
        numbers = re.findall(r'\d+', text)
        if numbers:
            return numbers[0]
    return None

def mappingRate(df, x):
    data = df[x]
    data = [np.nan if val == 'nan' else val for val in data]
    df = pd.DataFrame({'original_text': data})
    df['numbers'] = df['original_text'].apply(extract_numbers)
    df = df.dropna(subset=['numbers'])
    df['numbers'] = df['numbers'].astype(int)
    mapping_dict = dict(zip(df['original_text'], df['numbers']))
    # print(mapping_dict)
    return mapping_dict


def mappingTimes(df, x): 
    mapS = df[x].unique()
    pattern = r'(\d+)\s*-\s*(\d+)'
    mins = []
    maxs = []
    meds = []
    match_status = []

    for item in mapS:
        
      if isinstance(item, str):
      
        match = re.search(pattern, item)

        if match: 
            min_value = int(match.group(1))
            mins.append(min_value)
            max_value = int(match.group(2))
            maxs.append(max_value)
            # interval_mapping[item] = (min_value, max_value)
            match_status.append('Matched')
        else:
            mins.append(0)
            maxs.append(999999)
            meds = 0
            match_status.append('Not Matched')
      else:
        mins.append(None)
        maxs.append(None)
        match_status.append(None)

    mapMap = pd.DataFrame({'orig': mapS, 'match': match_status, 'minimum': mins, 
                           'maximum': maxs, 'mediums': meds}).dropna()
    mapMap['meds'] = 0.5 * (mapMap.maximum - mapMap.minimum) + mapMap.minimum
    matched_rows = mapMap[mapMap['match'] == 'Matched']
    mapTimes = dict(zip(matched_rows['orig'], matched_rows['meds']))
    return mapTimes

def mapping(df, x, path):
    os.chdir(os.path.join(path, 'mappings'))

    def load_mapping(file_prefix):
        df_map = pd.read_csv(f'{file_prefix}_mapping1.csv')
        mapping1 = dict(zip(df_map['original'], df_map['translated']))
        df_map = pd.read_csv(f'{file_prefix}_mapping2.csv')
        mapping2 = dict(zip(df_map['original'], df_map['translated']))
        return mapping1, mapping2

    group_simple = {'afford', 'mode', 'purp', 'gender', 'age', 'educ', 'employ', 'income'}
    group_time = {
        "nonpeakCar", "nonpeakTaxi", "nonpeakPT", "nonpeakMoto", "nonpeakBike", "nonpeakWalk",
        "peakCar", "peakTaxi", "peakPT", "peakMoto", "peakBike", "peakWalk",
        'walkBus', 'walkTrain', 'waitBus', 'waitTrain'
    }
    group_safety = {
        'perSafeCar', 'perSafeTaxi', 'perSafePT', 'perSafeMoto', 'perSafeBike', 'perSafeWalk',
        'psafeCar', 'psafeTaxi', 'psafePT', 'psafeMoto', 'psafeBike', 'psafeWalk',
        'accept', 'satisfy', 'reliable'
    }

    if x in group_simple:
        return load_mapping(x)
    elif x in group_time:
        mapping1 = mappingTimes(df, x)
        mapping2 = dict(zip(pd.read_csv('time_interval_mapping2.csv')['original'],
                            pd.read_csv('time_interval_mapping2.csv')['translated']))
    elif x in group_safety:
        mapping1 = mappingRate(df, x)
        mapping2 = dict(zip(pd.read_csv('safety_interval_mapping2.csv')['original'],
                            pd.read_csv('safety_interval_mapping2.csv')['translated']))
    else:
        mapping1 = mapping2 = {999: 999}

    return mapping1, mapping2