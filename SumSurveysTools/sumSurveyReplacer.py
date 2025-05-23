#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tools to replace unique responses

@author: panosgtzouras
National Technical University of Athens
Research project: SUM
"""

import pandas as pd
import random
from sumSurveyMapping import mapping
import numpy as np

def findUniqueTimes(df):
    udf = pd.concat([df['nonpeakCar'], df['nonpeakTaxi'], df['nonpeakPT'], df['nonpeakMoto'],
                     df['nonpeakBike'], df['nonpeakWalk'], 
                     df['peakCar'], df['peakTaxi'], df['peakPT'],
                     df['peakMoto'], df['peakBike'], df['peakWalk'],
                     df['walkBus'], df['walkTrain'], df['waitBus'], df['waitTrain']
                     ])
    print(udf.unique())

def findUniqueRatings(df):
    udf = pd.concat([df['perSafeCar'], df['perSafeTaxi'], df['perSafePT'],
                     df['perSafeMoto'], df['perSafeBike'], df['perSafeWalk'], df['psafeCar'], df['psafeTaxi'],
                     df['psafePT'], df['psafeMoto'], df['psafeBike'], df['psafeWalk'], df['accept'], df['satisfy']])
    print(udf.unique())

def rePlacer(df, x):
    
    # print(mapping(df, x)[0])
    # print(mapping(df, x)[1])
    
    df[x] = df[x].replace(mapping(df, x)[0]).replace(mapping(df, x)[1])

    print(df[x].unique())
    return df

def genRandomTime(time_interval):
    """
    Generate a random integer time within the specified time interval.
    This function handles two formats: 'HH:MM-HH:MM' and 'HH bis HH Uhr'.
    """
    try:
        # Handling the 'HH:MM-HH:MM' format
        if '-' in time_interval:
            start_time, end_time = time_interval.split('-')
            start_hour = int(start_time.split(':')[0])
            end_hour = int(end_time.split(':')[0])
        # Handling the 'HH bis HH Uhr' format
        elif 'bis' in time_interval:
            start_time, end_time = time_interval.split(' bis ')
            start_hour = int(start_time)
            end_hour = int(end_time.split(' ')[0])
            
            # Handling the 'Entre Xh et Yh' format
        elif 'Entre' in time_interval and 'et' in time_interval:
           time_interval = time_interval.replace('h', '')
           start_time, end_time = time_interval.split(' et ')
           start_hour = int(start_time.split('Entre ')[1])
           end_hour = int(end_time)    
        
        else:
            # If the format is unknown, return None
            return None

        # Generating a random integer time within the interval
        random_time = random.randint(start_hour, end_hour)

        return random_time
    except:
        # In case of any parsing error, return None
        return None
    
def valueTTimes(val):
    if val > 0 and val <= 15: return 1
    elif val>15 and val <= 30: return 2
    elif val>30 and val <= 45: return 3
    elif val>45 and val <= 60: return 4
    elif val>60 and val <= 75: return 5
    elif val>75 and val <= 90: return 6 
    elif val>90: return 7
    else: return np.nan

def valueAfford(val):
    if val > 0 and val <= 0.10: return 1
    elif val>0.10 and val <= 0.20: return 2
    elif val>0.20 and val <= 0.30: return 3
    elif val>0.30 and val <= 0.40: return 4
    elif val>0.40: return 5
    else: return np.nan

def valueWtimes(val):
    if val > 0 and val <= 5: return 1
    elif val>10 and val <= 15: return 2
    elif val>15 and val <= 25: return 3
    elif val>25 and val <= 30: return 4
    elif val>30 and val <= 35: return 5
    elif val>35 and val <= 40: return 6
    elif val>40 and val <= 45: return 7
    elif val>45 and val <= 50: return 8
    elif val>50 and val <= 55: return 9
    elif val>55: return 10
    else: return np.nan

def newAssessDF(df):
    assessDF = df.copy()
    for col in ['nonpeakCar', 'nonpeakTaxi', 'nonpeakPT', 'nonpeakMoto', 'nonpeakBike', 'nonpeakWalk',
                    'peakCar', 'peakTaxi', 'peakPT', 'peakMoto', 'peakBike', 'peakWalk']:
        assessDF[col] = assessDF[col].apply(valueTTimes)
    for col in ['afford']:
        assessDF[col] = assessDF[col].apply(valueAfford)
    for col in ['waitBus', 'waitTrain', 'walkBus', 'walkTrain']:
        assessDF[col] = assessDF[col].apply(valueWtimes)
    return assessDF

def fill_na_empirical(df, group_col, target_col):
    """
    Fill NaN values in the target_col based on the empirical distribution of each group in group_col.
    
    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        group_col (str): The column representing the grouping (e.g., 'city').
        target_col (str): The column with missing values to be filled.
    
    Returns:
        pd.DataFrame: Updated DataFrame with NaN values filled.
    """
    def sample_from_distribution(sub_df):
        non_na_values = sub_df.dropna().tolist()
        return sub_df.apply(lambda x: np.random.choice(non_na_values) if pd.isna(x) and non_na_values else x)

    df[target_col] = df.groupby(group_col)[target_col].transform(sample_from_distribution)
    return df

def sociodummies(df, categorical_cols = ["gender", "age", "educ", "employ"]):
    dummy_vars = pd.get_dummies(df[categorical_cols], prefix="", prefix_sep="").astype(int)
    df = pd.concat([df, dummy_vars], axis=1)
    return df

