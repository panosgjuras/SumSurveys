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
import geopandas as gpd
from scipy.spatial import distance_matrix
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
# TODO: fix the pathing, download the data from Zenodo
root_dir = "/Users/panosgtzouras/Desktop/datasets/csv/SUMsurveyData/finalDatasets"
color_map = {
    'car': '#004494',
    'taxi': '#FCF008',
    'train': '#dd8452',
    'bus': '#FF632F',
    'motorcycle': '#da8bc3',
    'bicycle': '#98C33A',
    'escooter': '#75BDFB',
    'walk': '#DADADA',
    'car sharing': '#2D8CFF',
    'micromobility': '#C4DD8B',
    'ride hailing': '#FFC2AF',
    'ferry': 'grey'
}
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

df2 = pd.read_csv(os.path.join(root_dir, "SumSurveyDiaries_v2.0.2.csv"))

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
print(len(df2))

version = "_v2.0.2"
df2.copy().to_csv(
    os.path.join(root_dir, f"SumSurveyDiaries{version}.csv"),
    index=False
) # this dataset is the same with V1 but it is the ex-post

# %%

# print(df1.columns)
# print(df2.columns)

exclude_cities = ['Fredrikstad', 'Larnaca', 'Rotterdam']
df1 = df1[~df1['city'].isin(exclude_cities)].copy()

# Distance bins: 0-5, 5-10, ..., 35-40, 40+
# bins = [0, 5, 10, 15, 20, 25, np.inf]
# labels = ['0-5', '5-10', '10-15', '15-20', '20-25',
#           '25+']

bins = [0, 2.5, 5, 7.5, 10, 12.5, 15, 17.5, 20, 22.5, 25, np.inf]

labels = [
    '0-2.5',
    '2.5-5',
    '5-7.5',
    '7.5-10',
    '10-12.5',
    '12.5-15',
    '15-17.5',
    '17.5-20',
    '20-22.5',
    '22.5-25',
    '25+'
]

def modeShareDistStats(df):
    temp = df.copy()

    temp['distance_bin'] = pd.cut(
        temp['distance'],
        bins=bins,
        labels=labels,
        right=False,
        include_lowest=True)

    counts = (
        temp
        .groupby(['distance_bin', 'mode'])
        .size()
        .reset_index(name='n'))

    counts['share'] = counts.groupby('distance_bin')['n'].transform(
        lambda x: 100 * x / x.sum()
    )

    pivot = counts.pivot(
        index='distance_bin',
        columns='mode',
        values='share'
    ).fillna(0)

    # keep distance bin order
    pivot = pivot.reindex(labels)

    return pivot

def is_dark(hex_color):
    r, g, b = mcolors.to_rgb(hex_color)
    luminance = 0.2126*r + 0.7152*g + 0.0722*b
    return luminance < 0.5

def stacked_ShareDist(df, title):
    pivot = modeShareDistStats(df)

    modes = [m for m in color_map.keys() if m in pivot.columns]
    pivot = pivot[modes]
    
    fig, ax = plt.subplots(figsize=(8, 8), dpi=300)
    
    pivot.plot(
        kind='bar',
        stacked=True,
        color=[color_map[m] for m in modes],
        width = 0.8,
        alpha = 0.8,
        edgecolor='black',
        ax=ax)
    
    ax.set_title(title)
    ax.set_xlabel('Distance band (km)')
    ax.set_ylabel('Mode share (%)')
    ax.set_ylim(0, 100)
    ax.legend(title='Transport mode', bbox_to_anchor=(1.02, 1), loc='upper left')

    # Annotate percentages
    for i, mode in enumerate(modes):
    
        color = color_map[mode]
        text_color = 'white' if is_dark(color) else 'black'
    
        for container in [ax.containers[i]]:
    
            labels_txt = [
                f'{v.get_height():.0f}%'
                if v.get_height() >= 5 else ''
                for v in container
            ]
    
            ax.bar_label(
                container,
                labels=labels_txt,
                label_type='center',
                fontsize=10,
                color=text_color,
#                fontweight = 'bold'
            )
            
    plt.tight_layout()
    plt.show()


remark = 'Rotterdam, Larnca, and Fredrikstad exluded'
stacked_ShareDist(df1, f"Ex-ante mode share ({remark})")
stacked_ShareDist(df2, f"Ex-post mode share ({remark})")


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


