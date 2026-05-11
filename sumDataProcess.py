#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 11 14:22:22 2026

@author: panosgtzouras
"""

import pandas as pd
import os

# TODO: fix package calling, create the init file
os.chdir("/Users/panosgtzouras/Desktop/github_tzouras/SumSurveys/SumSurveysTools")
from sumSurveyRenameSelect import callData, missCols, excludeCity
from sumSurveyReplacer import genRandomTime, rePlacer
from sumAssessAnalysis import plotModalSplit3
from sumSurveyModalShiftVisualize import stacked_ModeShare
from sumSurveyDiariesProc import createDiariesDf

import geopandas as gpd
from scipy.spatial import distance_matrix
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap, to_hex
import matplotlib as mpl
# TODO: fix the pathing, download the data from Zenodo
root_dir = "/Users/panosgtzouras/Desktop/datasets/csv/SUMsurveyData/finalDatasets"

# SumSurveyDiaries datasets
# _v1.0.1 ex-ante no distance, it is the same with V1 (Geneva is missing)
# _v1.0.2 ex-post no distance (Fredrikstad is missing)
# _v2.0.1 ex-ante with distances, it is the same with V2 (Geneva is missing)
# _v2.0.2 ex-post with distances (Fredrikstad, Larnaca and Rotterdam is missing)
# _v3.0.1 ex-ante with distance: all cities

# SumSurveySocio datasets
# _v1.0.1 ex-ante
# _v1.0.2 ex-post, but no information for income is provided


# %% New Functions

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

# %% Align the ex-ante dataset

df1 = pd.read_csv(os.path.join(root_dir, "SumSurveyDiariesV2.csv"))
print(df1.columns)

df1 = df1.drop(columns = ['orig_latitude', 'orig_longitude', 'dest_latitude', 'dest_longitude', 'distance'])
df1 = df1.rename(columns = {'fdistance':'distance'})
# Important the intra-zonal distance is set equal to 1
df1['distance'] = df1['distance'].replace(5, 1)

version = "_v1.0.1"
df1.copy().to_csv(
    os.path.join(root_dir, f"SumSurveyDiaries{version}.csv"),
    index=False
)

socio1 = pd.read_csv(os.path.join(root_dir, "SumSurveySocioV1.csv"))

# version = "_v1.0.1"
# socio1.copy().to_csv(
#     os.path.join(root_dir, f"SumSurveySocio{version}.csv"),
#     index=False
# ) # this dataset is the same with V1 but it is the ex-post

# %% ProcesS the dataset sent by Oskar

init_csv = "/Users/panosgtzouras/Library/CloudStorage/OneDrive-UniversityofWestAttica/TZOURAS_paperz/paper49_sumImpact/ex_ante_dataset/SumSurveyDiaries_FINAL_with_Demographics.csv"
df = pd.read_csv(init_csv)
# print(df.columns)
# print(df.survey_type.unique())

df_expost = df[df["survey_type"] == "ExPost"].copy() # keep only the expost to clean the mess
# print(df_expost.survey_type.unique())
# print(df_expost.shape)
#  df_expost.to_csv()
# print(df_expost.columns)

df2 = df_expost[
    ['mode', 'purp', 'time', 'orig', 'dest', 'pid', 'city',
     'orig_latitude', 'orig_longitude', 'dest_latitude', 'dest_longitude',
     'distance', 'fdistance']
].copy() # keep the  same columns


df2['time'] =  df2['time'].apply(genRandomTime)
df2 = rePlacer(df2, 'mode')
df2 = rePlacer(df2, 'purp')

version = "_v1.0.2"
df2[['mode', 'purp', 'time', 'pid', 'city']].copy().to_csv(
    os.path.join(root_dir, f"SumSurveyDiaries{version}.csv"),
    index=False
) # this dataset is the same with V1 but it is the ex-post

socio2 = df_expost[['pid', 'city', 'gender', 'age', 'education', 'employment']].copy()
socio2 = socio2.drop_duplicates(subset='pid').copy()
# Rename to match socio1
socio2 = socio2.rename(columns={'education': 'educ', 'employment': 'employ'})
socio2 = socio2[socio2['age'] >= 18].copy()
if 'income' not in socio2.columns: socio2['income'] = None # TODO: send a reminder to Oskar
char = ['gender', 'educ', 'age', 'employ', 'income']
for c in char: socio2 = rePlacer(socio2, c)

version = "_v1.0.2"
socio2.copy().to_csv(
    os.path.join(root_dir, f"SumSurveySocio{version}.csv"),
    index=False
) # this dataset is the same with V1 but it is the ex-post

# %% Add distances

centroids = gpd.read_file(
    os.path.join(root_dir, "geocoded_locations_v5.gpkg"),
    layer="locations")

distDf = createDistDf2(centroids)
distDf[distDf < 0.001] = 1 # This is the case of intra-zonal trips, they are assumed equal to 5 km

df2 = findTripDistances2(df2)
# print(df2.columns)
df2 = df2.drop(columns=['orig_latitude','orig_longitude', 'dest_latitude', 'dest_longitude', 
               'fdistance', 'orig2', 'dest2'])
# print(len(df2))
# Keep only rows with valid finite distances
df2 = df2[df2['distance'].notna() & np.isfinite(df2['distance'])].copy()
df2 = df2[
    df2['distance'].notna() &
    np.isfinite(df2['distance']) &
    (df2['distance'] <= 200)
].copy()
# print(len(df2))

version = "_v2.0.2"
df2.copy().to_csv(
    os.path.join(root_dir, f"SumSurveyDiaries{version}.csv"),
    index=False
) # this dataset is the same with V1 but it is the ex-post

# %% Fix Geneva set, what is going on there, check the data again

attr = [
        'orig1','dest1','mode1', 'time1', 'purp1', 
        'orig2','dest2','mode2', 'time2', 'purp2', 
        'orig3','dest3','mode3', 'time3', 'purp3',
        'orig4','dest4','mode4', 'time4', 'purp4', 
        'orig5','dest5','mode5', 'time5', 'purp5'] # origin and destination dimmension is not yet considered
col3 = ['pid', 'city'] + attr
diaries = pd.DataFrame(columns = col3)
path = "/Users/panosgtzouras/Desktop/datasets/csv/SUMsurveyData"
for c in ['Geneva','Munich']:
    df = callData(c, path, when = "finalBefore")[0]
    df = missCols(df, attr)
    diaries = pd.concat([diaries, df[col3]],ignore_index=True)

diaries = createDiariesDf(diaries) # now write all trips in row, each trip is one row
# so diaries now is a set of trips
diaries = rePlacer(diaries, 'mode') # replace the transport modes based on the mappings
diaries = rePlacer(diaries, 'purp') # replace the trip purposes based on the mappings
diaries['time'] =  diaries['time'].apply(genRandomTime) # generate travel times and other

# diaries.to_csv(
#     os.path.join("/Users/panosgtzouras/Desktop", 'munich_geneva_problem.csv'),
#     index=False
# ) # this dataset is the same with V1 but it is the ex-post
# centroids = gpd.read_file(
#     os.path.join(root_dir, "geocoded_locations_v5.gpkg"),
#     layer="locations"
# )

distDf = createDistDf2(centroids)
distDf[distDf < 0.001] = 1 # This is the case of intra-zonal trips, they are assumed equal to 5 km

diaries = findTripDistances2(diaries)
diaries = diaries.drop(columns=['orig2', 'dest2'])
diaries = diaries[diaries['distance'].notna() & np.isfinite(diaries['distance'])].copy()

df1 = pd.read_csv(os.path.join(root_dir, "SumSurveyDiaries_v2.0.1.csv"))
df1 = df1[df1['city'] != 'Munich'].copy() # remove past munich observations
df1 = pd.concat([df1, diaries], ignore_index=True) # append the new estimated diaries

version = "_v3.0.1"
df1.copy().to_csv(os.path.join(root_dir, f"SumSurveyDiaries{version}.csv"), index=False)


