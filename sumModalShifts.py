#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  5 13:47:32 2026

@author: panosgtzouras
"""

import pandas as pd
import os

# TODO: fix package calling, create the init file
os.chdir("/Users/panosgtzouras/Desktop/github_tzouras/SumSurveys/SumSurveysTools")
from sumSurveyReplacer import genRandomTime, rePlacer
from sumAssessAnalysis import plotModalSplit3
from sumSurveyModalShiftVisualize import stacked_ModeShare
import geopandas as gpd
from scipy.spatial import distance_matrix
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap, to_hex
import matplotlib as mpl
# TODO: fix the pathing, download the data from Zenodo
root_dir = "/Users/panosgtzouras/Desktop/datasets/csv/SUMsurveyData/finalDatasets"

# %% Import the before dataset

# TODO: fix the pathing, download the data from Zenodo
root_dir = "/Users/panosgtzouras/Desktop/datasets/csv/SUMsurveyData/finalDatasets"

df1 = pd.read_csv(os.path.join(root_dir, "SumSurveyDiariesV2.csv"))
print(df1.columns)

df1 = df1.drop(columns = ['orig_latitude', 'orig_longitude', 'dest_latitude', 'dest_longitude', 'distance'])
df1 = df1.rename(columns = {'fdistance':'distance'})
df1['distance'] = df1['distance'].replace(5, 1)

version = "_v2.0.1"
df1.copy().to_csv(
    os.path.join(root_dir, f"SumSurveyDiaries{version}.csv"),
    index=False
) # this dataset is the same with V1 but it is the ex-post


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


df2 = df_expost[
    ['mode', 'purp', 'time', 'orig', 'dest', 'pid', 'city',
     'orig_latitude', 'orig_longitude', 'dest_latitude', 'dest_longitude',
     'distance', 'fdistance']
].copy() # keep the  same columns


df2['time'] =  df2['time'].apply(genRandomTime)
df2 = rePlacer(df2, 'mode')
df2 = rePlacer(df2, 'purp')

# version = "_v2.0.2"
# df2.copy().to_csv(
#     os.path.join(root_dir, f"SumSurveyDiaries{version}.csv"),
#     index=False
# ) # this dataset is the same with V1 but it is the ex-post

version = "_v1.0.2"
df2[['mode', 'purp', 'time', 'pid', 'city']].copy().to_csv(
    os.path.join(root_dir, f"SumSurveyDiaries{version}.csv"),
    index=False
) # this dataset is the same with V1 but it is the ex-post

# %% Classic pies

cIE = df2.city.unique() # Fredrikstad is missing from the data
for c in cIE: plotModalSplit3(df2, c) # Develop the classical modal split pies

# %% Add distance

centroids = gpd.read_file(
    os.path.join(root_dir, "geocoded_locations_v3.gpkg"),
    layer="locations"
)

# df2 = pd.read_csv(os.path.join(root_dir, "SumSurveyDiaries_v2.0.2.csv"))

def createDistDf2(centroids):
    # make sure CRS is WGS84 first
    centroids = centroids.set_crs("EPSG:4326", allow_override=True)
    # project to meters
    centroids_m = centroids.to_crs("EPSG:3857")
    coords = centroids_m.geometry.apply(lambda geom: (geom.x, geom.y)).tolist()
    dist_matrix = distance_matrix(coords, coords)
    # convert meters to km and apply detour factor
    dist_matrix = (1.3 * dist_matrix) / 1000
    zone_codes = centroids_m['location']
    dist_df = pd.DataFrame(
        dist_matrix,
        index=zone_codes,
        columns=zone_codes
    )
    return dist_df

distDf = createDistDf2(centroids)
distDf[distDf < 0.001] = 1 # This is the case of intra-zonal trips, they are assumed equal to 5 km

def get_distance(orig_zone, dest_zone):
    try:
        return distDf.at[orig_zone, dest_zone]
    except KeyError:
        return None

def findTripDistances2(df):
    df['orig2'] = df['orig'].astype(str) + ", " + df['city']
    df['dest2'] = df['dest'].astype(str) + ", " + df['city']
    df['distance'] = df.apply(
        lambda row: get_distance(row['orig2'], row['dest2']),
        axis=1
    )
    return df

df2 = findTripDistances2(df2)
# print(df2.columns)
df2 = df2.drop(columns=['orig_latitude','orig_longitude', 'dest_latitude', 'dest_longitude', 
               'fdistance', 'orig2', 'dest2'])
print(len(df2))
# Keep only rows with valid finite distances
df2 = df2[df2['distance'].notna() & np.isfinite(df2['distance'])].copy()
df2 = df2[
    df2['distance'].notna() &
    np.isfinite(df2['distance']) &
    (df2['distance'] <= 200)
].copy()
print(len(df2))

version = "_v2.0.2"
df2.copy().to_csv(
    os.path.join(root_dir, f"SumSurveyDiaries{version}.csv"),
    index=False
) # this dataset is the same with V1 but it is the ex-post

# %%

df1 = pd.read_csv(os.path.join(root_dir, "SumSurveyDiaries_v2.0.1.csv"))
df2 = pd.read_csv(
    os.path.join(root_dir, "SumSurveyDiaries_v2.0.2.csv")
)

# exclude_cities = ['Fredrikstad', 'Larnaca', 'Rotterdam', 'Geneva', 'Jerusalem']
# df1 = df1[~df1['city'].isin(exclude_cities)].copy() # no data about distance in the ex-post
# df2 = df2[~df2['city'].isin(exclude_cities)].copy() # no data about distance in the ex-post

# Distance bins: 0-5, 5-10, ..., 35-40, 40+
# bins = [0, 5, 10, 15, 20, 25, np.inf]
# labels = ['0-5', '5-10', '10-15', '15-20', '20-25',
#           '25+']

city_colors = {
    'Munich': '#004494',        
    'Geneva': '#98C33A',        
    'Jerusalem': '#FF632F',
    'Athens': '#75BDFB',
    'Rotterdam': '#2D8CFF',     
    'Krakow': '#dd8452',        
    'Fredrikstad': '#da8bc3',   
    'Larnaca': '#FFC2AF',       
    'Coimbra': '#DADADA'}

bins = [0, 2.5, 5, 7.5, 10, 12.5, 15, 17.5, 20, 22.5, 25, np.inf]

labels = ['0-2.5', '2.5-5', '5-7.5', '7.5-10', '10-12.5',
          '12.5-15', '15-17.5', '17.5-20', '20-22.5', '22.5-25', '25+']

stacked_ModeShare(
    df=df1, x_col='distance', stack_col='city', title='Ex-ante mode share by distance',
    x_title='Trip distance (km)', stack_col_colors=city_colors, 
    x_bins=bins,
    x_labels=labels)

stacked_ModeShare(
    df=df2, x_col='distance', stack_col='city', title='Ex-post mode share by distance',
    x_title='Trip distance (km)', stack_col_colors=city_colors, 
    x_bins=bins,
    x_labels=labels)

stacked_ModeShare(
    df=df1, x_col='purp', stack_col='city', title='Ex-ante mode share by trip purpose',
    x_title='Trip purpose', stack_col_colors=city_colors, 
    x_bins=None,
    x_labels=None)

stacked_ModeShare(
    df=df2, x_col='purp', stack_col='city', title='Ex-ante mode share by trip purpose',
    x_title='Trip purpose', stack_col_colors=city_colors, 
    x_bins=None,
    x_labels=None)

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
char = ['gender', 'age', 'educ', 'employ', 'income']
for c in char: socio2 = rePlacer(socio2, c)

