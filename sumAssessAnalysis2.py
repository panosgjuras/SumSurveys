root_dir = "/Users/panosgtzouras/Desktop/datasets/csv/SUMsurveyData"

import os
import pandas as pd
import matplotlib.pyplot as plt
# import seaborn as sns
import numpy as np

from sumSurveyReplacer import sociodummies

import biogeme.database as db
import biogeme.biogeme as bio
import biogeme.messaging as msg
from biogeme import models
from biogeme.expressions import (Beta,
    bioDraws,
    PanelLikelihoodTrajectory,
    MonteCarlo,
    log,)
from statsmodels.stats.outliers_influence import variance_inflation_factor

import seaborn as sns

def criticalBarsHor(diaries, var, color_map, xlabel = "", normalize = True, agg_method = "sum"):
    """
    Function to create the critical bars of Sum Survey paper: class vs city, 
    mode vs class and mode vs city.

    Parameters:
        diaries : pandas.DataFrame
            A DataFrame containing travel diary data: mode, class, city.

        var : str
            The column name used for grouping the data (e.g., city name).

        sumx : str
            The column name containing passenger distance values to be aggregated.

        color_map : dict
            A dictionary mapping transport modes to specific colors for visualization.

    Returns:
        None
        Displays a stacked horizontal bar chart with percentage annotations.
    """
    if agg_method == "sum":
        sumx = 'fdistance'
        df_grouped = diaries.groupby(var)[sumx].sum().unstack().fillna(0)
    elif agg_method == "count":
        sumx = 'pid'
        df_grouped = diaries.groupby(var)[sumx].nunique().unstack().fillna(0)
    else:
        raise ValueError("agg_method must be 'sum' or 'count'")
        
    if normalize:
        df_grouped = df_grouped.div(df_grouped.sum(axis=1), axis=0) * 100
    
    # Filter colors for available modes in the data
    available_modes = df_grouped.columns
    colors = [color_map[mode] for mode in available_modes if mode in color_map]

    # Plot with higher DPI
    fig, ax = plt.subplots(figsize=(8, 12), dpi=500)
    df_grouped.plot(kind='barh', stacked=True, color=colors, alpha=0.7, ax=ax)


    # Annotate bars
    for i, city in enumerate(df_grouped.index):
        cumulative_width = 0  
        for mode in df_grouped.columns:
            value = df_grouped.loc[city, mode]
            if (normalize and value > 5) or (not normalize and value > df_grouped.sum().max() * 0.02):  
                ax.text(cumulative_width + value / 2, i, f"{value:.1f}" + ("%" if normalize else ""), 
                        ha='center', va='center', fontsize=10, color='black', fontweight='bold')
            cumulative_width += value  

    # Labels and title
    ax.set_ylabel("")  # Variable name as y-axis label
    ax.set_xlabel(xlabel)
    ax.legend(title="Transport mode", bbox_to_anchor=(1.05, 1), loc='upper left')

    # Show plot
    plt.show()

def boxFactorPlot(ax, df, factor, city_col, ylim = [0, 100]):
    """
    Creates a box plot for the given factor, with cities on the x-axis.
    
    Parameters:
    df (DataFrame): The dataset containing the factor and city column.
    factor (str): The column name of the factor to plot.
    city_col (str): The column name representing the cities.
    
    Returns:
    None (Displays the plot)
    """
    plt.figure(figsize=(10, 10), dpi = 500)
    sorted_cities = sorted(df[city_col].unique())
    
    sns.boxplot(x=df[city_col], y=df[factor], order = sorted_cities,
                color = "#FF632F", ax = ax)

    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)  # Rotate city names for better readability
    ax.set_xlabel("")
    ax.set_ylim(ylim)
    ax.set_ylabel(factor.replace("_", " ").title() + " score")
#    plt.title(f"Box Plot of {factor.replace('_', ' ').title()} by City")

    ax.grid(axis="y", linestyle="--", alpha=0.7)

def MNLest(df, V, av, cho, name):
    logprob = models.loglogit(V, av, cho) # import utilities in loglogit
    # logger = msg.bioMessage() 
    # logger.setDetailed()  
    biogeme = bio.BIOGEME(df, logprob) # estimate biogeme based on the defined database
    biogeme.calculateNullLoglikelihood(av)
    biogeme.modelName = name
    results = biogeme.estimate()
    p = results.getEstimatedParameters()
    return p

def checkVIF(df):
    """
    Calculates the Variance Inflation Factor (VIF) for a selected set of variables.

    Parameters:
    - df (pd.DataFrame): The original dataframe.
    - selected_vars (list): List of column names to compute VIF for.

    Returns:
    - pd.DataFrame: DataFrame with variable names and their corresponding VIF values.
    """

    numeric_df = df.select_dtypes(include=["number"]).dropna()  # Keep only numeric columns
    vif_data = pd.DataFrame()
    vif_data["Feature"] = numeric_df.columns
    vif_data["VIF"] = [variance_inflation_factor(numeric_df.values, i) for i in range(len(numeric_df.columns))]
    
    # print(vif_data)
    return vif_data.sort_values(by="VIF", ascending=False)

class betas:
    def __init__(self, mean, mink, maxk, st):
        ######
        # ASC_CAR = Beta('ASC_CAR', mean, mink, maxk, st)
        self.ASC_CAR = Beta('ASC_CAR', mean, mink, maxk, st)
        self.ASC_NO_CAR = Beta('ASC_NO_CAR', mean, mink, maxk, st)
        
        ######
        self.DIST = Beta('BETA_DIST', mean, mink, maxk, st)
        self.WORK = Beta('BETA_WORK', mean, mink, maxk, st)
        self.FACTOR_1 = Beta('BETA_FACTOR_1', mean, mink, maxk, st)
        self.FACTOR_2 = Beta('BETA_FACTOR_2', mean, mink, maxk, st)
        self.FACTOR_3 = Beta('BETA_FACTOR_3', mean, mink, maxk, st)
        self.FACTOR_4 = Beta('BETA_FACTOR_4', mean, mink, maxk, st)
        self.FACTOR_5 = Beta('BETA_FACTOR_5', mean, mink, maxk, st)
#        self.FACTOR_5 = Beta('BETA_FACTOR_6', mean, mink, maxk, st)
        
        self.CLASS_1 = Beta('BETA_CLASS_1', mean, mink, maxk, st)
        self.CLASS_2 = Beta('BETA_CLASS_2', mean, mink, maxk, st)
        self.CLASS_3 = Beta('BETA_CLASS_3', mean, mink, maxk, st)
        self.CLASS_4 = Beta('BETA_CLASS_4', mean, mink, maxk, st)
        
        self.MUN = Beta('BETA_MUNICH', mean, mink, maxk, st)
        self.ATH = Beta('BETA_ATHENS', mean, mink, maxk, st)
        self.ROT = Beta('BETA_ROTTERDAM', mean, mink, maxk, st)
        self.LAR = Beta('BETA_LARNACA', mean, mink, maxk, st)
        self.FRE = Beta('BETA_FREDRIKSTAD', mean, mink, maxk, st)
        self.COI = Beta('BETA_COIMBRA', mean, mink, maxk, st)
        self.JER = Beta('BETA_JERUSALEM', mean, mink, maxk, st)
        self.KRA = Beta('BETA_KRAKOW', mean, mink, maxk, st)

class utils:
    def __init__(self, dbs, b):
        
        self.set_MNL(dbs, b)
        
        self.set_modecho_av()
        self.set_cho(dbs)
  
    def set_MNL(self, dbs, b):
        globals().update(dbs.variables)
        V0 = 0
        V1 = (
#               b.ASC_CAR 
               b.DIST * fdistance + b.WORK * work

             + b.FACTOR_1 * factor_1 
             + b.FACTOR_2 * factor_2 
             + b.FACTOR_3 * factor_3 
             + b.FACTOR_4 * factor_4
             + b.FACTOR_5 * factor_5

             + b.CLASS_2 * class_2
             + b.CLASS_3 * class_3
             + b.CLASS_4 * class_4
             
             + b.MUN * Munich
             + b.ATH * Athens + b.ROT * Rotterdam 
             + b.LAR * Larnaca + b.FRE * Fredrikstad
             + b.COI * Coimbra + b.JER * Jerusalem
             + b.KRA * Krakow
              
              )
        V = {0: V0, 1: V1}
        self.__MNL = V
    
    def get_MNL(self): 
        return self.__MNL
    
    def set_modecho_av(self): self.__av = {0:1, 1:1}
    
    def get_modecho_av(self):
        return self.__av
        
    def set_cho(self, dbs):
            globals().update(dbs.variables)
            self.__cho = carchoice
            
    def get_cho(self): 
        return self.__cho

diaries = pd.read_csv(os.path.join(root_dir,'finalDatasets','SumSurveyDiariesV2.csv'))
diaries['fdistance'] = diaries['fdistance'].replace({5:2})
diaries['mode'] = diaries['mode'].replace({'water taxi':'car'}) 

socio = pd.read_csv(os.path.join(root_dir,'finalDatasets','SumSurveySocioV3.csv'))
socio["s_class"] = "class " + socio["class"].astype('str')  
# diaries.to_csv(os.path.join(root_dir,'finalDatasets','SumSurveyDiariesV2.csv'))

assess = pd.read_csv(os.path.join(root_dir, "finalDatasets", "SumSurveyAssessV6.csv"))

# Define the color map
color_map_mode = {
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

color_map_class = {
    "class 1": '#75BDFB',
    "class 2": '#A9D7FD',
    "class 3": '#B5DC7A',
    "class 4": '#98C33A'}

diaries['cityhier'] = diaries['city'].replace({'Munich': '1: Munich',
                                               'Athens': '2: Athens',
                                               'Coimbra': '8: Coimbra',
                                               'Krakow': '5: Krakow',
                                               'Larnaca': '7: Larnaca',
                                               'Jerusalem': '3: Jerusalem',
                                               'Fredrikstad': '6: Fredrikstad',
                                               'Rotterdam': '4: Rotterdam'})

df = pd.merge(diaries[['pid','city','cityhier','purp','mode','fdistance']], 
              socio[['pid', 'class', 's_class']], on = 'pid')

df = pd.merge(df, assess[['pid', 'factor_1', 'factor_2', 'factor_3', 
                          'factor_4', 'factor_5']], on = 'pid')

criticalBarsHor(df, ['cityhier', 'mode'], color_map_mode, xlabel = 'percentage (%) of passenger kilometers')

criticalBarsHor(df, ['cityhier', 's_class'], color_map = color_map_class,
                xlabel = 'Number of respondents', normalize = False, agg_method = "count")

#for f in ['factor_1', 'factor_2', 'factor_3', 'factor_4', 'factor_5']:
#     boxFactorPlot(df, f, 'cityhier')

# Create 3x2 grid of subplots
fig, axes = plt.subplots(3, 2, figsize=(15, 20), dpi=500)

# Create the box plots in the 3x2 grid
boxFactorPlot(axes[0, 0], df, 'factor_1', 'cityhier', ylim=[0, 25])
boxFactorPlot(axes[0, 1], df, 'factor_2', 'cityhier', ylim=[-15, 15])
boxFactorPlot(axes[1, 0], df, 'factor_3', 'cityhier', ylim=[-15, 15])
boxFactorPlot(axes[1, 1], df, 'factor_4', 'cityhier', ylim=[0, 10])
boxFactorPlot(axes[2, 0], df, 'factor_5', 'cityhier', ylim=[0, 80])

fig.delaxes(axes[2,1])

# Adjust layout
plt.tight_layout()
plt.show()



# criticalBars(df, ['s_class', 'mode'], 'fdistance', color_map_mode)

df['class_1'] = np.where(df['class'] == 1, 1, 0)
df['class_2'] = np.where(df['class'] == 2, 1, 0)
df['class_3'] = np.where(df['class'] == 3, 1, 0)
df['class_4'] = np.where(df['class'] == 4, 1, 0)

df['carchoice'] = np.where(df['mode'] == 'car', 1, 0)

df['work'] = np.where(df['purp'].isin(["work", "education"]), 1, 0)

df = df[['pid', 'city', 'carchoice', 'work','fdistance', 'factor_1', 'factor_2',
         'factor_3', 'factor_4', 'factor_5', 
         'class_1', 'class_2', 'class_3', 'class_4']]

df = sociodummies(df, categorical_cols = ['city'] )

checkVIF(df.drop(columns = ['class_1', 'pid', 'carchoice']))
# exclude = 'factor_3'
# checkVIF(df.drop(columns = ['Munich', 'pid', 'factor_4', 'class_1', 'factor_1', 'class_4']))

name = "sumSurvey_General_v3.3.4"
database = db.Database('sumSurvey_General', df.drop(columns = ["pid", 'city']))
b = betas(0, -1000, 1000, 0)
u = utils(database, b)
p = MNLest(database, u.get_MNL(), u.get_modecho_av(), u.get_cho(), name)
out_dir = "/Users/panosgtzouras/Library/CloudStorage/OneDrive-UniversityofWestAttica/TZOURAS_paperz/paper32_SumSurvey/results_March_2025"
p.to_csv(os.path.join(out_dir, name + ".csv"))

# for c in df.city.unique():
#    name = "sumSurvey_" + c
#    cdf = df.loc[df['city'] == c]
#   database = db.Database("sumSurvey_" + c, cdf.drop(columns = ["pid", 'city']))
#    b = betas(0, -1000, 1000, 0)
#    u = utils(database, b)
#    p = MNLest(database, u.get_MNL(), u.get_modecho_av(), u.get_cho(), name)

# checkVIF(df, df.drop(columns = ["pid", 'city']).columns)

# # List of categorical columns
# categorical_cols = ["gender", "age", "educ", "employ", "income"]

# # Create an empty list to store results
# dfs = []

# # Loop through each categorical column and compute percentages
# for col in categorical_cols:
#     ct = pd.crosstab(socio[col], socio["class"])  # Convert to percentages
#     ct = ct.reset_index().melt(id_vars=col, var_name="class", value_name="percentage")  # Reshape
#     ct = ct.rename(columns={col: "category"})  # Rename for consistency
#     dfs.append(ct)

# # Combine all into one DataFrame
# final_df = pd.concat(dfs, ignore_index=True)

# # Display the final table
# print(final_df.head())

# # Pivot the table to get classes as columns
# final_df_wide = final_df.pivot_table(index="category", columns="class", values="percentage").reset_index()

# # Rename columns to make them clearer
# final_df_wide.columns.name = None  # Remove multi-index
# final_df_wide = final_df_wide.rename(columns=lambda x: f"class_{x}" if isinstance(x, int) else x)

# # Display the transformed DataFrame
# print(final_df_wide.head())

