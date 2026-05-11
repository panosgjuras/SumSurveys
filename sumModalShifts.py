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

# %% Classic pies of modal split

version = "_v3.0.1"

cIE = ('Munich','Geneva', 'Jerusalem', 'Athens', 'Rotterdam', 'Krakow',    
       'Fredrikstad', 'Larnaca','Coimbra')

for c in cIE:
    for v in ["_v3.0.1", "_v1.0.2"]:
        df = pd.read_csv(os.path.join(root_dir, f"SumSurveyDiaries{v}.csv"))
        plotModalSplit3(df, c) 
 
# %% Analyze based on trip distance and trip purpose

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
#          '27.5-30', '30+']

for v, t in zip(["_v3.0.1", "_v2.0.2"],["Ex-ante", "Ex-post"]):
    df = pd.read_csv(os.path.join(root_dir, f"SumSurveyDiaries{v}.csv"))
    stacked_ModeShare(
        df = df, 
        x_col='distance', 
        stack_col='city', 
        title=f"{t} mode share by distance ({len(df)} trips)",
        x_title='Trip distance (km)', 
        stack_col_colors=city_colors, 
        x_bins=bins,
        x_labels=labels)


for v, t in zip(["_v3.0.1", "_v1.0.2"],["Ex-ante", "Ex-post"]):
    df = pd.read_csv(os.path.join(root_dir, f"SumSurveyDiaries{v}.csv"))
    stacked_ModeShare(
        df = df.sort_values(by='purp').copy(), 
        x_col='purp', 
        stack_col='city', 
        title=f"{t} mode share by trip purpose ({len(df)} trips)",
        x_title='Trip purpose', 
        stack_col_colors=city_colors, 
        x_bins=None,
        x_labels=None)

# %%


for x in ['gender', 'educ', 'age', 'employ']:
    rename_map = {'educ': 'education', 'employ': 'employment'}
    x1 = rename_map.get(x, x)
    
    for v1, v2, t2 in zip(["_v3.0.1", "_v1.0.2"], 
                          ["_v1.0.1", "_v1.0.2"],
                          ["Ex-ante", "Ex-post"]):
        df = pd.read_csv(os.path.join(root_dir, f"SumSurveyDiaries{v1}.csv"))
        socio = pd.read_csv(os.path.join(root_dir, f"SumSurveySocio{v2}.csv"))
#       socio = socio.drop_duplicates(subset='pid').copy()
        df = df.merge(socio[['pid', x]].copy(), 
                            on='pid', how='left')
        df = df[df[x].notna()].copy()
        stacked_ModeShare(
            df=df.sort_values(by=x).copy(), 
            x_col=x, 
            stack_col='city', 
            title= f"{t2} mode share vs {x1} ({len(df)} trips)",
            x_title='', 
            stack_col_colors=city_colors, 
            x_bins=None,
            x_labels=None)
