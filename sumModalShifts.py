#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  5 13:47:32 2026

@author: panosgtzouras
"""

import pandas as pd
import os

# TODO: fix package calling
os.chdir("/Users/panosgtzouras/Desktop/github_tzouras/SumSurveys/SumSurveysTools")
from sumSurveyReplacer import genRandomTime, rePlacer
from sumAssessAnalysis import plotModalSplit3
# import geopandas as gpd

# TODO: fix the pathing, download the data from Zenodo
root_dir = "/Users/panosgtzouras/Desktop/datasets/csv/SUMsurveyData/finalDatasets"

# %% Import the before dataset

# TODO: fix the pathing, download the data from Zenodo
root_dir = "/Users/panosgtzouras/Desktop/datasets/csv/SUMsurveyData/finalDatasets"

df1 = pd.read_csv(os.path.join(root_dir, "SumSurveyDiariesV2.csv"))
print(df1.columns)

socio1 = pd.read_csv(os.path.join(root_dir, "SumSurveySocioV1.csv"))
# print(socio1.columns)

# %%

# TODO: remove this section, it is not necessary
init_csv = "/Users/panosgtzouras/Library/CloudStorage/OneDrive-UniversityofWestAttica/TZOURAS_paperz/paper49_sumImpact/ex_ante_dataset/SumSurveyDiaries_FINAL_with_Demographics.csv"

df = pd.read_csv(init_csv)
# print(df.columns)
# print(df.survey_type.unique())

df_expost = df[df["survey_type"] == "ExPost"].copy() # keep only the expost to clean the mess
# print(df_expost.survey_type.unique())
# print(df_expost.shape)
#  df_expost.to_csv()
# print(df_expost.columns)
# %% Harmonize the dataset with ex-post

# SumSurveyDiaries datasets
# _v1.0.1 ex-ante no distance, it is the same with V1
# _v1.0.2 ex-post no distance
# _v2.0.1 ex-ante with distances, it is the same with V2
# _v2.0.2 ex-post with distances
version = "_v1.0.2"

df2 = df_expost[
    ['mode', 'purp', 'time', 'orig', 'dest', 'pid', 'city',
     'orig_latitude', 'orig_longitude', 'dest_latitude', 'dest_longitude',
     'distance', 'fdistance']
].copy() # keep the  same columns


df2['time'] =  df2['time'].apply(genRandomTime)
df2 = rePlacer(df2, 'mode')
df2 = rePlacer(df2, 'purp')

df2[['mode', 'purp', 'time', 'pid', 'city']].copy().to_csv(
    os.path.join(root_dir, f"SumSurveyDiaries{version}.csv"),
    index=False
) # this dataset is the same with V1 but it is the ex-post

# %% Classic pies

df2 = pd.read_csv(os.path.join(root_dir, "SumSurveyDiaries_v1.0.2.csv"))
cIE = df2.city.unique() # Fredrikstad is missing from the data
for c in cIE: plotModalSplit3(df2, c) # Develop the classical modal split pies

# %% Add distance

df2.to_csv(
    os.path.join(root_dir, "SumSurveyDiariesV2.0.2.csv"),
    index=False
)


# %% Create the socio dataframe

socio2 = df_expost[
    ['pid', 'city', 'gender', 'age', 'education', 'employment']
].copy()

# Rename to match socio1
socio2 = socio2.rename(columns={
    'education': 'educ',
    'employment': 'employ'
})

# If income exists in socio1 but not in df_expost, add it as NaN
if 'income' not in socio2.columns:
    socio2['income'] = None

# Reorder columns to match socio1 exactly
socio2 = socio2[['pid', 'city', 'gender', 'age', 'educ', 'employ', 'income']]

# print(socio2.columns)
# print(socio2.shape)


