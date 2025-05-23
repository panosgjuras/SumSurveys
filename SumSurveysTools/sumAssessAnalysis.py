#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data analysis and visualization functions

@author: panosgtzouras
National Technical University of Athens
Research project: SUM
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from scipy.stats import kendalltau
from scipy import stats
from itertools import combinations
from scipy.stats import mannwhitneyu
import numpy as np
import os

end_color_rgb = (148, 191, 65)  # RGB for light green
start_color_rgb = (35, 79, 145)     # RGB for deep blue

# Function to interpolate between two colors
def interpolate_colors(color1, color2, n=100):
    color1 = np.array(color1)
    color2 = np.array(color2)
    return [tuple(np.linspace(color1[i], color2[i], n)) for i in range(3)]

# Interpolating between the start and end colors
r, g, b = interpolate_colors(start_color_rgb, end_color_rgb)
palette_rgb = [tuple([r[i], g[i], b[i]]) for i in range(len(r))]

# Normalizing the RGB values to the 0-1 range for display
palette_rgb_normalized = [tuple([x/255.0 for x in color]) for color in palette_rgb]

# Displaying the palette
# sns.palplot(palette_rgb_normalized)
# plt.show()


def dstatsAssess(data, filepath):
    # Calculate descriptive statistics for each city
    stats_by_city = data.groupby('city').describe()
    # Save to a CSV file
    with pd.ExcelWriter(filepath) as writer:
        stats_by_city.to_excel(writer)
    return stats_by_city


def acceptHist2(df, city):
    relevant_data = df[['city', 'accept']].dropna()
    city_data = relevant_data[relevant_data['city'] == city]['accept']
    plt.figure(figsize=(10, 6))

    # Histogram
    n, bins, patches = plt.hist(city_data, bins=[0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5], 
                                color='#98C33A', edgecolor='black', alpha=0.6, density=True)

    # Kernel Density Estimation
    sns.kdeplot(city_data, color='#004494', linewidth=2, bw_adjust=1.25)

    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.0%}'.format(y)))
    plt.title(f'4: Acceptance of policies in {city}')
    plt.xlabel('Share (%)')
    plt.ylabel('Percentage')
    plt.xticks([1, 2, 3, 4, 5, 6])
    plt.show()

# Example usage
# acceptHist(your_dataframe, 'Your City')


def acceptHist(df, city):
    relevant_data = df[['city', 'accept']].dropna()
    city_data = relevant_data[relevant_data['city'] == city]['accept']
    plt.figure(figsize=(10, 6))
    n, bins, patches = plt.hist(city_data, bins=[0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5], 
                                color='#98C33A', edgecolor='black', alpha=0.6, density=True)
    plt.plot((bins[:-1] + bins[1:]) / 2, n, color='#004494', linestyle='-', linewidth=2)
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.0%}'.format(y)))
    plt.title(f'4: Acceptace of policies in {city}')
    plt.xlabel('')
    plt.ylabel('Percentage')
    plt.xticks([1, 2, 3, 4, 5, 6])
    plt.show()


def satisfyHist(df, city):
    relevant_data = df[['city', 'satisfy']].dropna()
    city_data = relevant_data[relevant_data['city'] == city]['satisfy']
    plt.figure(figsize=(10, 6))

    # Histogram
    n, bins, patches = plt.hist(city_data, bins=[0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5], 
                                color='#75BDFB', edgecolor='black', alpha=0.6, density=True)

    # Kernel Density Estimation
    sns.kdeplot(city_data, color='#004494', linewidth=2, bw_adjust=1.25)

    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.0%}'.format(y)))
    plt.title(f'5: Satisfaction in {city}')
    plt.xlabel('Share (%)')
    plt.ylabel('Percentage')
    plt.xticks([1, 2, 3, 4, 5, 6])
    plt.show()    
    
    
def heatmapTimeSafe(data, city, custom_yticks = [7.5, 22.5, 37.5, 52.5, 67.5, 82.5, 95.0], 
                    custom_ytick_labels = ["0-15", "15-30", "30-45", "45-60", "60-75", "75-90", "> 90"],
                    custom_xticks = [1, 2, 3, 4, 5, 6], 
                    custom_xtick_labels = ["1: very unsafe", "2", "3", "4", "5", "6: very safe"]):
    modes = ["Car", "Taxi", "PT", "Moto", "Bike", "Walk"]
    fig, axes = plt.subplots(3, 2, figsize=(15, 20))  # 3 rows, 2 columns for the subplots
    axes = axes.flatten()  # Flatten the 2D array of axes for easy iteration
    # Now, we'll create a heatmap for each mode of transportation as a subplot
    for i, mode in enumerate(modes):
        # Extract mode-specific columns
        peak_col = f'peak{mode}' 
        psafe_col = f'psafe{mode}'
        mode_data = data[data['city'] == city][[peak_col, psafe_col]].dropna()
        
        all_combinations = pd.MultiIndex.from_product([custom_yticks, custom_xticks], names=['mode', 'time'])
        complete_grid = pd.DataFrame(index=all_combinations).reset_index()
        
        # Group the data to get the frequency of each combination
        grouped_data = mode_data.groupby([peak_col, psafe_col]).size().unstack(fill_value=0)
        
        # Create the heatmap in the corresponding subplot axis
        sns.heatmap(grouped_data, annot=True, cmap= palette_rgb_normalized, fmt='g', ax=axes[i])  # Using reversed crest palette
        axes[i].set_title(f'{mode} mode in {city}')
        axes[i].set_xlabel('Perceived safety')
        axes[i].set_ylabel('Travel time at peak hours in mins')
        
        axes[i].set_xticks(np.arange(len(custom_xticks)) + 0.5)
        axes[i].set_xticklabels(custom_xtick_labels, rotation=45)
        axes[i].set_yticks(np.arange(len(custom_yticks)) + 0.5)
        axes[i].set_yticklabels(custom_ytick_labels)
        # axes[i].set_xtick(np.arange(len(custom_yticks)) + 0.5, custom_ytick_labels)
    # Adjust the layout to prevent overlap
    plt.tight_layout()
    plt.show()
        
def plotModalSplit3(dataframe, city, angel = 60):
    """
    Plots a pie chart without labels for slices less than 1%, and with percentage annotations for slices greater than 1%.
    """
    city_data = dataframe[dataframe['city'] == city]
    mode_counts = city_data['mode'].value_counts()

    # Define color map
    # Define color map
    color_map = {'car': '#004494',
                 'taxi': '#FCF008',
                 'train':'#dd8452',
                 'bus': '#FF632F',
                 'motorcycle': '#da8bc3',
                 'bicycle': '#98C33A',
                 'escooter': '#75BDFB',
                 'walk': '#DADADA',
                 'car sharing': '#2D8CFF',
                 'micromobility': '#C4DD8B', 
                 'ride hailing': '#FFC2AF',
                 'ferry':'grey'}

    colors = [color_map[mode] for mode in mode_counts.index if mode in color_map]

    # Set thresholds
    explode_threshold = 0.10  # 10%
    label_threshold = 0.005  # 1%
    total = sum(mode_counts)

    explode = [0.1 if (count / total) < explode_threshold else 0 for count in mode_counts]

    def autopct_format(values):
        def my_format(pct):
            return ('%.1f%%' % pct) if pct > label_threshold * 100 else ''
        return my_format

    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(mode_counts, labels=None, autopct=autopct_format(mode_counts), startangle=angel, colors=colors, explode=explode)

    # Label only slices greater than the label_threshold
    for i, (wedge, count) in enumerate(zip(wedges, mode_counts)):
        if (count / total) > label_threshold:
            angle = (wedge.theta2 + wedge.theta1) / 2
            x = np.cos(np.deg2rad(angle))
            y = np.sin(np.deg2rad(angle))
            horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
            connectionstyle = f"angle,angleA=0,angleB={angle}"
            ax.annotate(mode_counts.index[i], xy=(x, y), xytext=(1.2*np.sign(x), 1.2*y),
                       horizontalalignment=horizontalalignment,
                       arrowprops=dict(arrowstyle="->", connectionstyle=connectionstyle, color='black'))

    ax.axis('equal')
    plt.title(f"Modal split in {city}")
    plt.show()



def heatmapModeTime(data, city, xk = 7, yk = 7):
    
    custom_yticks = ['car', 'taxi', 'train', 'bus', 'motorcycle', 'bicycle', 'escooter', 
                     'walk', 'car sharing','micromobility','ride hailing', 'ferry'], 
    custom_xticks = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 
                           16, 17, 18, 19, 20, 21, 22, 23]
    
    mode_data = data[data['city'] == city][['mode', 'time']].dropna()
    fig, ax = plt.subplots(figsize=(xk,yk))
    grouped_data = mode_data.groupby(['mode', 'time']).size().unstack(fill_value=0)
    sns.heatmap(grouped_data, annot=True, cmap= palette_rgb_normalized, fmt='g', ax=ax)
    ax.set_xlabel('Trip mode')    
    ax.set_ylabel('Time of the day')
    ax.set_xticks(np.arange(len(custom_xticks)) + 0.5)
    ax.set_yticks(np.arange(len(custom_yticks)) + 0.5)    
    plt.title(f'{city}')
    plt.show


def prepareHeatMap(mode_data, custom_yticks, custom_xticks, peak_col_name, psafe_col_name, type = 'perecentage'):
    """
    Prepares data for a heatmap by calculating the percentage distribution across specified categories.

    Parameters:
    - mode_data (pd.DataFrame): DataFrame containing the data for a specific mode of transportation.
    - custom_yticks (list): List of y-axis tick values.
    - custom_xticks (list): List of x-axis tick values.
    - peak_col_name (str): Column name for peak hour data.
    - psafe_col_name (str): Column name for perceived safety data.

    Returns:
    - pd.DataFrame: Data prepared for heatmap plotting.
    """
    # Create all possible combinations of yticks and xticks
    all_combinations = pd.MultiIndex.from_product([custom_yticks, custom_xticks], names=[peak_col_name, psafe_col_name])
    complete_grid = pd.DataFrame(index=all_combinations).reset_index()
    
    # Merge with the actual data and fill missing combinations with zero
    merged_data = pd.merge(complete_grid, mode_data.groupby([peak_col_name, psafe_col_name]).size().reset_index(name='count'), 
                           on=[peak_col_name, psafe_col_name], how='left').fillna(0)
    
    # Calculate the percentage for each combination
    total_count = merged_data['count'].sum()
    merged_data['percentage'] = (merged_data['count'] / total_count)

    # Pivot the data to create a heatmap-friendly format
    heatmap_data = merged_data.pivot(peak_col_name, psafe_col_name, 'percentage')
    
    return heatmap_data

def heatmapTimeSafe2(data, city, custom_yticks = [7.5, 22.5, 37.5, 52.5, 67.5, 82.5, 95.0], 
                    custom_ytick_labels = ["0-15", "15-30", "30-45", "45-60", "60-75", "75-90", "> 90"],
                    custom_xticks = [1, 2, 3, 4, 5, 6], 
                    custom_xtick_labels = ["1: very unsafe", "2", "3", "4", "5", "6: very safe"]):
    
    modes = ["Car", "Taxi", "PT", "Moto", "Bike", "Walk"]
    fig, axes = plt.subplots(3, 2, figsize=(15 * 0.75 , 27.5 * 0.75))  # 3 rows, 2 columns for the subplots
    axes = axes.flatten()  # Flatten the 2D array of axes for easy iteration
    
    # Now, we'll create a heatmap for each mode of transportation as a subplot
    
    for i, mode in enumerate(modes):
        # Extract mode-specific columns
        peak_col = f'peak{mode}' 
        psafe_col = f'psafe{mode}'
        mode_data = data[data['city'] == city][[peak_col, psafe_col]].dropna()
        
        # all_combinations = pd.MultiIndex.from_product([custom_yticks, custom_xticks], names=[peak_col, psafe_col])
        # complete_grid = pd.DataFrame(index=all_combinations).reset_index()
        
        # merged_data = pd.merge(complete_grid, mode_data.groupby([peak_col, psafe_col]).size().reset_index(name='count'), 
        #                       on=[peak_col, psafe_col], how='left').fillna(0)
        
        # total_count = merged_data['count'].sum()
        # merged_data['percentage'] = (merged_data['count'] / total_count)

        # heatmap_data = merged_data.pivot(peak_col, psafe_col, 'percentage')
        
        heatmap_data = prepareHeatMap(mode_data, custom_yticks, custom_xticks, peak_col, psafe_col)
        
        sns.heatmap(heatmap_data, annot=True, cmap= palette_rgb_normalized, ax = axes[i], fmt=".1%", cbar=False)
                 
        axes[i].set_title(f'{mode} mode in {city}')
        axes[i].set_xlabel('Perceived safety')
        axes[i].set_ylabel('Travel time at peak hours in mins')
        
        axes[i].set_xticks(np.arange(len(custom_xticks)) + 0.5)
        axes[i].set_xticklabels(custom_xtick_labels, rotation=45)
        axes[i].set_yticks(np.arange(len(custom_yticks)) + 0.5)
        axes[i].set_yticklabels(custom_ytick_labels)
        # axes[i].set_xtick(np.arange(len(custom_yticks)) + 0.5, custom_ytick_labels)
    # Adjust the layout to prevent overlap
    plt.tight_layout()
    plt.show()

def heatmapPeakOff(data, city, custom_yticks = [7.5, 22.5, 37.5, 52.5, 67.5, 82.5, 95.0], 
                    custom_ytick_labels = ["0-15", "15-30", "30-45", "45-60", "60-75", "75-90", "> 90"]):
    
    custom_xticks = custom_yticks
    custom_xtick_labels = custom_ytick_labels
    
    modes = ["Car", "Taxi", "PT", "Moto", "Bike", "Walk"]
    fig, axes = plt.subplots(3, 2, figsize=(15 * 0.75 , 25 * 0.75))  # 3 rows, 2 columns for the subplots
    axes = axes.flatten()  # Flatten the 2D array of axes for easy iteration
    for i, mode in enumerate(modes):
        # Extract mode-specific columns
        peak_col = f'peak{mode}' 
        nonpeak_col = f'nonpeak{mode}'
        mode_data = data[data['city'] == city][[peak_col, nonpeak_col]].dropna()
        
        # all_combinations = pd.MultiIndex.from_product([custom_yticks, custom_xticks], names=[peak_col, psafe_col])
        # complete_grid = pd.DataFrame(index=all_combinations).reset_index()
        
        # merged_data = pd.merge(complete_grid, mode_data.groupby([peak_col, psafe_col]).size().reset_index(name='count'), 
        #                       on=[peak_col, psafe_col], how='left').fillna(0)
        
        # total_count = merged_data['count'].sum()
        # merged_data['percentage'] = (merged_data['count'] / total_count)

        # heatmap_data = merged_data.pivot(peak_col, psafe_col, 'percentage')
        
        heatmap_data = prepareHeatMap(mode_data, custom_yticks, custom_xticks, peak_col, nonpeak_col)
        
        sns.heatmap(heatmap_data, annot=True, cmap= palette_rgb_normalized, ax = axes[i], fmt=".1%", cbar=False)
                 
        axes[i].set_title(f'{mode} mode in {city}')
        axes[i].set_xlabel('Travel time at non peak hours in mins')
        axes[i].set_ylabel('Travel time at peak hours in mins')
        
        axes[i].set_xticks(np.arange(len(custom_xticks)) + 0.5)
        axes[i].set_xticklabels(custom_xtick_labels, rotation=45)
        axes[i].set_yticks(np.arange(len(custom_yticks)) + 0.5)
        axes[i].set_yticklabels(custom_ytick_labels)
        # axes[i].set_xtick(np.arange(len(custom_yticks)) + 0.5, custom_ytick_labels)
    # Adjust the layout to prevent overlap
    plt.tight_layout()
    plt.show()


def heatmapModeTime2(data, city, xk=15, yk=4):
    custom_yticks = ['car', 'taxi', 'train', 'bus', 'motorcycle', 'bicycle', 'escooter', 
                     'walk', 'car sharing', 'micromobility', 'ride hailing', 'ferry']
    custom_xticks = list(range(24))  # 0 to 23 hours

    # Filter data for the specified city
    mode_data = data[data['city'] == city][['mode', 'time']].dropna()

    # Create a complete grid of mode-time combinations
    all_combinations = pd.MultiIndex.from_product([custom_yticks, custom_xticks], names=['mode', 'time'])
    complete_grid = pd.DataFrame(index=all_combinations).reset_index()

    # Merge the complete grid with the actual data
    merged_data = pd.merge(complete_grid, mode_data.groupby(['mode', 'time']).size().reset_index(name='count'), 
                           on=['mode', 'time'], how='left').fillna(0)

    # Pivot the data for heatmap
    heatmap_data = merged_data.pivot('mode', 'time', 'count')

    # Plotting
    fig, ax = plt.subplots(figsize=(xk, yk))
    sns.heatmap(heatmap_data, annot=True, cmap= palette_rgb_normalized, fmt='g', ax=ax, cbar=False)
    ax.set_xlabel('Time of the Day')
    ax.set_ylabel('Transport Mode')
    # ax.set_xticks(np.arange(len(custom_xticks)) + 0.5, labels=custom_xticks)
    # ax.set_yticks(np.arange(len(custom_yticks)) + 0.5, labels=custom_yticks)    
    plt.title(f'Modal split vs Time in {city}')
    plt.show()

# Example usage: heatmapModeTime(dataframe, 'Rotterdam', 10, 10)
# Replace 'dataframe' and 'Rotterdam' with your actual DataFrame and city name.

def heatmapModePurp(data, city, xk=15, yk=4):
    custom_yticks = ['car', 'taxi', 'train', 'bus', 'motorcycle', 'bicycle', 'escooter', 
                     'walk', 'car sharing', 'micromobility', 'ride hailing', 'ferry']
    custom_xticks = ['work', 'home', 'education', 'shopping', 'recreation', 
                      'health', 'services', 'other' ]

    # Filter data for the specified city
    mode_data = data[data['city'] == city][['mode', 'purp']].dropna()
    print(mode_data)

    # Create a complete grid of mode-time combinations
    all_combinations = pd.MultiIndex.from_product([custom_yticks, custom_xticks], names=['mode', 'purp'])
    complete_grid = pd.DataFrame(index=all_combinations).reset_index()

    # Merge the complete grid with the actual data
    merged_data = pd.merge(complete_grid, mode_data.groupby(['mode', 'purp']).size().reset_index(name='count'), 
                           on=['mode', 'purp'], how='left').fillna(0)

    # Pivot the data for heatmap
    heatmap_data = merged_data.pivot('mode', 'purp', 'count')

    # Plotting
    fig, ax = plt.subplots(figsize=(xk, yk))
    sns.heatmap(heatmap_data, annot=True, cmap= palette_rgb_normalized, fmt='g', ax=ax, cbar=False)
    ax.set_xlabel('Trip purpose')
    ax.set_ylabel('Transport Mode')
    # ax.set_xticks(np.arange(len(custom_xticks)) + 0.5, labels=custom_xticks)
    # ax.set_yticks(np.arange(len(custom_yticks)) + 0.5, labels=custom_yticks)    
    plt.title(f'Modal split vs Trip purpose in {city}')
    plt.show()


def kolmogoTest(data1, data2, var):
    ks_statistic, p_value = stats.ks_2samp(data1[var], data2[var])
    alpha = 0.05
    if p_value > alpha:
        decision = 'The distributions of Data 1 and Data 2 are similar (fail to reject H0)'
    else:
        decision = 'The distributions of Data 1 and Data 2 are different (reject H0)'
    return ks_statistic, p_value, decision

def kolmoTable(assess, sele, filepath, cIE = ['Athens', 'Munich', 'Rotterdam', 'Larnaca', 'Krakow', 'Fredrikstad',
                                              'Geneva','Coimbra', 'Jerusalem'] ):
    df = pd.DataFrame(columns=['city1', 'city2', 'variable', 'ks_statistic', 'p_value', 'decision'])
    
    for city1, city2 in combinations(cIE, 2):
        data1 = assess[assess['city'] == city1]
        data2 = assess[assess['city'] == city2]        
        for var in sele:
            # print(f"Processing {city1} vs {city2}, variable: {var}")
            try:
                c = kolmogoTest(data1, data2, var) 
                df = df.append({'city1': city1, 'city2': city2, 'variable': var, 'ks_statistic': c[0],
                                'p_value': c[1], 'decision': c[2]}, ignore_index=True)
            except Exception as e:
                 print(f"Error occurred: {e}")
            continue
        
        
    print("Finished processing")
    
    with pd.ExcelWriter(filepath) as writer:
        df.to_excel(writer)
    
    return df

def DistRtable(data):

    # Create a pivot table to represent the distribution comparison
    pivot_table = data.pivot_table(index='city1', columns='city2', values='variable', aggfunc=lambda x: ', '.join(x))

    # Filter out the variables where the decision is 'similar'
    similar_variables = data[data['decision'] == 'The distributions of Data 1 and Data 2 are similar (fail to reject H0)']

    # Initialize the table to store similar distribution variables
    similar_distribution_table = pd.DataFrame(index=pivot_table.index, columns=pivot_table.columns)

    # Iterate through each city pair in the pivot table
    for city1 in pivot_table.index:
        for city2 in pivot_table.columns:
            # Get the variables with similar distribution for the current city pair
            similar_vars = similar_variables[(similar_variables['city1'] == city1) & (similar_variables['city2'] == city2)]['variable'].values
            # Join the variables into a single string separated by comma
            similar_vars_str = ', '.join(similar_vars)
            # Store the similar distribution variables in the table
            similar_distribution_table.at[city1, city2] = similar_vars_str

    return similar_distribution_table



def perform_kendall_tau(df, variables, alpha=0.05):    
    
    df = df.dropna()
    
    num_vars = len(variables)
    results = []
    
    for i in range(num_vars):
        for j in range(i+1, num_vars):
            
            var1_name = variables[i]
            var2_name = variables[j]
            
            var1 = df[var1_name]
            var2 = df[var2_name]
            
            # Perform Kendall's Tau correlation test
            tau, p_value = kendalltau(var1, var2)
            
            result = {
                'Variable 1': var1_name,
                'Variable 2': var2_name,
                'Tau': tau,
                'P-value': p_value,
                'Significant': 'Yes' if p_value < alpha else 'No'
            }
            results.append(result)
            
    results_df = pd.DataFrame(results)
    return results_df


def corrTable(prdf, sele, filepath, alpha = 0.05):    
    df = perform_kendall_tau(prdf, sele, alpha = alpha)

    pivot_table = df.pivot_table(index='Variable 1', columns='Variable 2', values='Tau')
    similar_variables = df[df['Significant'] == 'Yes']
    # similar_variables['Tau'] = pd.to_numeric(similar_variables['Tau'], errors='coerce')
    similar_distribution_table = pd.DataFrame(index=sele, columns=sele)  # Ensure unique indices and columns
    
    for var1 in pivot_table.index:
        for var2 in pivot_table.columns:
            similar_vars = similar_variables[(similar_variables['Variable 1'] == var1) & (similar_variables['Variable 2'] == var2)]['Tau'].values
            mean_value = similar_vars.mean() if len(similar_vars) > 0 else None
            similar_distribution_table.at[var1, var2] = mean_value
    
    for i in range(len(sele)):
        for j in range(i+1, len(sele)):
            var1 = sele[i]
            var2 = sele[j]
            similar_distribution_table.at[var2, var1] = similar_distribution_table.at[var1, var2]
    
    
    # Convert the DataFrame to float dtype
    similar_distribution_table = similar_distribution_table.astype(float)
    
    with pd.ExcelWriter(filepath) as writer:
        similar_distribution_table.to_excel(writer)

    return similar_distribution_table

def visualizeCorr(corr_table, x = 1.75):
    
    start_color_rgb = (148, 191, 65)  # RGB for light green
    end_color_rgb = (35, 79, 145)     # RGB for deep blue
    
    r, g, b = interpolate_colors(start_color_rgb, end_color_rgb)
    palette_rgb = [tuple([r[i], g[i], b[i]]) for i in range(len(r))]

    # Normalizing the RGB values to the 0-1 range for display
    palette_rgb_normalized = [tuple([x/255.0 for x in color]) for color in palette_rgb]
    
    plt.figure(figsize=(10 * x, 10 * x))
    sns.set_style("darkgrid")
    sns.heatmap(corr_table, annot=True, cmap=palette_rgb_normalized, fmt=".2f",
                linecolor = 'black',
                vmin = -1, vmax = 1,
                annot_kws={"size": 12}, cbar=False)
    plt.title('Correlation Table')
    plt.xlabel('')
    plt.ylabel('')
    plt.xticks(fontsize=12)  # Increase x-axis tick font size
    plt.yticks(fontsize=12)  # Increase y-axis tick font size
    plt.show()
    
    
def mannWhitney(df1,df2, alpha = 0.05):
    statistic, p_value = mannwhitneyu(df1, df2)
    if p_value < alpha:
        decide = 'significant'
    else:
       decide = 'not significant'
    return statistic, p_value, decide

def finCompare(df, asse, sele, modes):
    for m in modes: df[m] = df['mode'].apply(lambda x: 1 if x == m else 0)
    df = pd.merge(df, asse, on = 'pid', how = 'inner')
    fin = pd.DataFrame(columns = ['variable'] + modes)
    fin.variable = sele
    fin = fin.set_index('variable')
    for m in modes:
        zeroDF = df[df[m] == 0]
        oneDF = df[df[m] == 1]
        for var in fin.index:
            xx = oneDF[var].dropna()
            yy = zeroDF[var].dropna()
            diff = np.mean(xx) - np.mean(yy)
            # print(diff)
            dec = mannWhitney(xx,yy)[2]
            diff = diff if dec == 'significant' else None
            fin.at[var, m] = diff
    fin = fin.astype(float)
    return fin
            
def visualizeCompare(df, asse, sele, modes, x = 1.75):
    df = finCompare(df, asse, sele, modes)
    
    start_color_rgb = (148, 191, 65)  # RGB for light green
    end_color_rgb = (35, 79, 145)     # RGB for deep blue
    r, g, b = interpolate_colors(start_color_rgb, end_color_rgb)
    palette_rgb = [tuple([r[i], g[i], b[i]]) for i in range(len(r))]
    # Normalizing the RGB values to the 0-1 range for display
    palette_rgb_normalized = [tuple([x/255.0 for x in color]) for color in palette_rgb]
    
    plt.figure(figsize=(5 * x, 10 * x))
    sns.set_style("darkgrid")
    sns.heatmap(df, annot=True, cmap=palette_rgb_normalized, fmt=".3f",
                linecolor = 'black',
                vmin = -1.5, vmax = 1.5,
                annot_kws={"size": 12}, cbar=False)
    plt.title('')
    plt.xlabel('Transport mode (1, if it is used)', fontsize=12)
    plt.ylabel('Variable', fontsize=12)
    plt.xticks(fontsize=12)  # Increase x-axis tick font size
    plt.yticks(fontsize=12)  # Increase y-axis tick font size
    plt.show()