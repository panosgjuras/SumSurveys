#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  7 13:33:33 2026

@author: panosgtzouras
"""

import pandas as pd
# import os
# from sumSurveyReplacer import genRandomTime, rePlacer
# from sumAssessAnalysis import plotModalSplit3
# import geopandas as gpd
# from scipy.spatial import distance_matrix
# import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
# from matplotlib.colors import LinearSegmentedColormap, to_hex
# import matplotlib as mpl

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

city_colors = {
    'Munich': '#004494',        # car
    'Geneva': '#98C33A',        # bicycle
    'Jerusalem': '#FF632F',     # bus
    'Athens': '#75BDFB',       # escooter
    'Rotterdam': '#2D8CFF',     # car sharing
    'Krakow': '#dd8452',        # train
    'Fredrikstad': '#da8bc3',   # motorcycle
    'Larnaca': '#FFC2AF',       # ride hailing
    'Coimbra': '#DADADA'        # walk
}

def modeShareStats(df, x_col):
    temp = df.copy()

    counts = (
        temp
        .groupby([x_col, 'mode'])
        .size()
        .reset_index(name='n')
    )

    counts['share'] = counts.groupby(x_col)['n'].transform(
        lambda x: 100 * x / x.sum()
    )

    pivot = (
        counts
        .pivot(index=x_col, columns='mode', values='share')
        .fillna(0)
    )

    return pivot


def is_dark(hex_color):
    r, g, b = mcolors.to_rgb(hex_color)
    luminance = 0.2126*r + 0.7152*g + 0.0722*b
    return luminance < 0.5


# df: the dataframe 
# x_col : the x variable that will be used in top figuges
# y_col: the y variable that will be used in the bottom figure
# stack_col: the categorical variable that will be used for coloring the bottom figure
# title: the title of the entire figure,
# stack_col_colors: the color band of the stack_col
# x_bins: the x_bins, if None then find the unique categories
# x_labels: the x_labels, if None use the unique categories


def stacked_ModeShare(df, x_col, stack_col, title, x_title=None,
                      stack_col_colors=None, x_bins=None, x_labels=None):
    """
    Create a two-panel visualization of transport mode shares and trip counts.

    The function generates:
    1. A 100% stacked bar chart showing modal shares across categories/bins, e.g., distance or city.
    2. A stacked histogram showing the number of trips per category,
       colored by a selected second categorical variable, e.g., city, or sociodemographic group.

    Parameters
    ----------
    df : pandas.DataFrame
        Input trip diary dataframe. Must contain:
        - 'mode'
        - 'pid'

    x_col : str
        Variable used for the x-axis in both figures.

    stack_col : str
        Categorical variable used for coloring the bottom stacked histogram.

    title : str
        Title of the full figure.

    x_title : str, optional
        Custom x-axis title.
        If None, x_col is used.

    stack_col_colors : dict, optional
        Dictionary mapping categories of stack_col to colors.

    x_bins : list, optional
        Bin edges for numerical x-axis variables.

        If provided, x_col is discretized using pd.cut().

        Example:
        [0, 5, 10, 15, 20, np.inf]

    x_labels : list, optional
        Labels corresponding to x_bins.

        Example:
        ['0-5', '5-10', '10-15', '15-20', '20+']

    Returns
    -------
    None
        Displays the figure using matplotlib.

    Notes
    -----
    - The upper figure always shows modal shares (%).
    - The lower figure always shows trip counts.
    - Percentages below 5% are not annotated.
    - If x_bins is None, categories are inferred automatically from x_col.

    Example
    -------
    stacked_ModeShare(
        df=df2,
        x_col='distance',
        stack_col='city',
        title='Ex-post mode share by distance',
        x_title='Trip distance (km)',
        stack_col_colors=city_colors,
        x_bins=[0, 5, 10, 15, 20, np.inf],
        x_labels=['0-5', '5-10', '10-15', '15-20', '20+']
    )
    """  

    temp = df.copy()

    # Create x-axis categories
    if x_bins is not None:
        temp['_x_cat'] = pd.cut(
            temp[x_col],
            bins=x_bins,
            labels=x_labels,
            right=False,
            include_lowest=True
        )
        x_axis = '_x_cat'
        x_order = x_labels
    else:
        x_axis = x_col
        x_order = temp[x_col].dropna().unique()

    # Top figure: mode share by x-axis category
    counts = (
        temp
        .groupby([x_axis, 'mode'])
        .size()
        .reset_index(name='n')
    )

    counts['share'] = counts.groupby(x_axis)['n'].transform(
        lambda x: 100 * x / x.sum()
    )

    pivot = (
        counts
        .pivot(index=x_axis, columns='mode', values='share')
        .fillna(0)
        .reindex(x_order)
    )

    modes = [m for m in color_map.keys() if m in pivot.columns]
    pivot = pivot[modes]

    # Bottom figure: y_col aggregated by x_axis and stack_col
    bottom_counts = (
        temp
        .groupby([x_axis, stack_col])['pid']
        .count()
        .reset_index(name='value')
    )

    bottom_pivot = (
        bottom_counts
        .pivot(index=x_axis, columns=stack_col, values='value')
        .fillna(0)
        .reindex(x_order)
    )

    fig, (ax, ax_bottom) = plt.subplots(
        2, 1,
        figsize=(8, 10),
        dpi=300,
        sharex=True,
        gridspec_kw={'height_ratios': [3, 1]}
    )

    # Top plot
    pivot.plot(
        kind='bar',
        stacked=True,
        color=[color_map[m] for m in modes],
        width=0.8,
        alpha=0.6,
        edgecolor='black',
        ax=ax
    )
    

    shared_modes = ['car sharing', 'micromobility', 'ride hailing']
    
    for i, mode in enumerate(modes):
    
        if mode in shared_modes:
    
            for patch in ax.containers[i]:
                patch.set_edgecolor('black')
                patch.set_linewidth(2.5)

    ax.set_title(title)
    ax.set_ylabel('Mode share (%)')
    ax.set_ylim(0, 100)

    ax.legend(
        title='Transport mode',
        bbox_to_anchor=(1.02, 1),
        loc='upper left'
    )

    # Annotate percentages
    for i, mode in enumerate(modes):

        text_color = 'white' if is_dark(color_map[mode]) else 'black'
        container = ax.containers[i]

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
            color=text_color
        )

    # Bottom plot colors
    if stack_col_colors is not None:
        colors = [
            stack_col_colors.get(c, '#DADADA')
            for c in bottom_pivot.columns
        ]
    else:
        colors = None

    bottom_pivot.plot(
        kind='bar',
        stacked=True,
        width=0.8,
        alpha=1,
        edgecolor='white',
        color=colors,
        ax=ax_bottom
    )

    for container in ax_bottom.containers:
        for bar in container:
            bar.set_hatch('////')
    
    if x_title is None: x_title = x_col

    ax_bottom.set_xlabel(x_title)
    ax_bottom.set_ylabel('Trips')

    ax_bottom.legend(
        title=stack_col,
        bbox_to_anchor=(1.02, 1),
        loc='upper left'
    )

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    
    
# stacked_ModeShare(
#     df=df1, x_col='distance', stack_col='city', title='Ex-ante mode share by distance',
#     x_title='Trip distance (km)', stack_col_colors=city_colors, 
#     x_bins=bins,
#     x_labels=labels)