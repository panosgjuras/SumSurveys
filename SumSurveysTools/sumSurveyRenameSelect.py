#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rename and select tools

@author: panosgtzouras
National Technical University of Athens
Research project: SUM
"""

import os
import pandas as pd
import numpy as np
# from sumSurveyFixLarnaca import fixLarnaca
from sumSurveyFixCoimbra import fixCoimbra
from sumSurveyCityParams import pidValue, droper

def callMatcher(df, city, path):
    saveColsPath = os.path.join(path, 'questionsMatch', 'matcher' + city + '.csv')
    delm = ","
    matcher = pd.read_csv(saveColsPath, delimiter = delm)
    # matcher = pd.read_csv(saveColsPath, delimiter=';')
    return matcher

def reNamer(df, city):
    matcher = callMatcher(df, city)
    # print(matcher)
    # matcher.loc[1, 'name2'] = 'found'
    matcher = matcher[matcher['name2'] != 'NotFound'].reset_index(drop = True)
    for i in range(0 , len(matcher)):
        df = df.rename(columns = {matcher.loc[i, 'fix']: matcher.loc[i, 'name2']})
    return df

def reSelect(df, city):
    matcher = callMatcher(df, city)
    select = pd.DataFrame(matcher.name2)
    select = select[select['name2'] != 'NotFound'].reset_index(drop = True)
    mask = df.columns.isin(select['name2'].tolist())
    df = df[df.columns[mask]]
    # df.loc[:,'pid'] = range(1 + pidValue(city), len(df) + 1 + pidValue(city))
    # df.loc[:, 'city'] = city
    # saveDatPath = os.path.join(root_dir, 'selectDataset', 'selectDataset' + city + '.csv')
    # df.to_csv(saveDatPath, index = False, encoding = encode(city)  )
    return df

def callData(city, path, when ="", match = 'yes'):
    
    if (city == 'Athens' or city == 'Munich' or city == 'Krakow' or city == 'Larnaca' or city == 'Geneva' or city == 'Jerusalem'): 
            file_path = os.path.join(path, 'rawDatasets' , city, when,'surveyDataset.xlsx')
            data = pd.read_excel(file_path)
            # Save as CSV
            csv_file_path = file_path.replace('.xlsx', '.csv')
            data.to_csv(csv_file_path, index=False)
            df = pd.read_csv(csv_file_path, header = None)
            # df = pd.read_csv(os.path.join(root_dir, 'sampleDatasets' , city, 'surveyDataset.csv'), delimiter=delm,
            #                 header = None)
            # print(df)

    if city == 'Fredrikstad': # save the variables columns
        file_path = os.path.join(path, 'rawDatasets' , city, when,'surveyDataset.xlsx')
        tab_name = 'Complete'
        data = pd.read_excel(file_path, sheet_name=tab_name)
        csv_file_path = file_path.replace('.xlsx', '.csv')
        data.to_csv(csv_file_path, index=False)
        df = pd.read_csv(csv_file_path, header = None)
    
    if city == 'Rotterdam':
        file_path = os.path.join(path, 'rawDatasets' , city, when, 'surveyDataset.xlsx')
        csv_file_path = file_path.replace('.xlsx', '.csv')
        df = pd.read_csv(csv_file_path, header = None)
    
    if city == 'Coimbra':
        file_path = os.path.join(path, 'rawDatasets' , city, when,'surveyDataset.xlsx')
        data = pd.read_excel(file_path)
        data = fixCoimbra(data)
        # Save as CSV
        csv_file_path = file_path.replace('.xlsx', '.csv')
        data.to_csv(csv_file_path, index=False)
        df = pd.read_csv(csv_file_path, header = None)
        # print(df)
        # df = pd.read_csv(os.path.join(root_dir, 'sampleDatasets' , city, 'surveyDataset.csv'), delimiter=delm,
        #                 header = None)
        # print(df)
    
    if match == 'yes':
        matcher = callMatcher(df, city)
        # print(matcher)
        df = reNamer(df, city)
        # print(df.head)
        df = reSelect(df, city)
        # print(df.head)
        df = droper(df, city)
        
        # if city == 'Larnaca':
        #    df = fixLarnaca(df)
    else: matcher = 0
    

    df.loc[:,'pid'] = range(1 + pidValue(city), len(df) + 1 + pidValue(city))
    df.loc[:, 'city'] = city
    # print(df)
    
    
    # if city == 'Larnaca':
    #    df = fixLarnaca(df)
        
       
    if city == 'Jerusalem':
        df = df.drop(df.index[0])
    
    return df, matcher

def saveCols(df, city, path, maxx = 1):
    first_row = df.iloc[0:1]
    
    name = 'columns' + city + '.xlsx'
    link = os.path.join(path, 'questionsMatch', name)
    first_row.to_excel(link, index=False)

def missCols(df, columns):
    """
    Add missing columns to the DataFrame with NaN values.

    :param df: Pandas DataFrame.
    :param columns: List of columns to check and add if missing.
    :return: DataFrame with the missing columns added.
    """
    for col in columns:
        if col not in df.columns:
            df[col] = np.nan
    return df

def excludeCity (df, cIE, cit):
    filtered_df = df[df['city'] != cit]
    if 'Geneva' in cIE: cIE = cIE.remove(cit)
    return filtered_df, cIE



