
import pandas as pd

import os
import numpy as np
from factor_analyzer import FactorAnalyzer
from sklearn.decomposition import PCA
from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity
from factor_analyzer.factor_analyzer import calculate_kmo
import matplotlib.pyplot as plt

# %% Main functions

def fillAssessNans(df, cols_with_nans, city_col='city'):
    """
    Replaces NaN values in specified columns with random samples drawn 
    from the distribution of non-NaN values within the same city.

    Parameters:
    - df (pd.DataFrame): The input dataframe
    - cols_with_nans (list): List of column names where NaNs should be replaced
    - city_col (str): Name of the column indicating the city

    Returns:
    - pd.DataFrame: Updated dataframe with NaNs filled
    """
    df = df.copy()  # To avoid modifying the original dataframe

    for col in cols_with_nans:
        for city in df[city_col].unique():
            # Select non-NaN values for the current city
            non_nan_values = df.loc[df[city_col] == city, col].dropna().values

            if len(non_nan_values) > 0:  # Ensure there's data to sample from
                # Generate random samples from existing values
                random_samples = np.random.choice(non_nan_values, size=df.loc[(df[city_col] == city) & df[col].isna(), col].shape[0], replace=True)
                
                # Replace NaNs with sampled values
                df.loc[(df[city_col] == city) & df[col].isna(), col] = random_samples

    return df  # Return the updated dataframe

# def factorAna(X, n):
# #    np.random.seed(42)
#     fa = FactorAnalyzer(n_factors = n, rotation="varimax")
#     fa.fit(X)
    
#     loadings = pd.DataFrame(fa.loadings_, index=X.columns)
#     print(loadings)
    
#     variance_explained = fa.get_factor_variance()
#     print(f"Variance Explained per Factor:\n{variance_explained[1]}")
#     print(f"Cumulative Variance Explained: {variance_explained[2][-1]:.2f}")
#     return fa, loadings

def relativeVars(df, refmode = "Car", asModes = ["Taxi", "PT", "Moto", "Bike", "Walk"]):
    for m in asModes:
        df["relnonpeak" + m] = df["nonpeak" + m]/df["nonpeak" + refmode]
        df["relpeak" + m] = df["peak" + m]/df["peak" + refmode]
        df["diffperSafe" + m] = df["perSafe" + m] - df["perSafe" + refmode]
        df["diffpsafe" + m] = df["psafe" + m] - df["psafe" + refmode]
    return df

# def removeLoads(loadings, threshold = 0.3, n_factors=6):

#     # Step 1: Identify variables to drop based on the threshold
#     low_loading_vars = []

#     # Calculate factor loadings using the FactorAnalyzer
#     fa = FactorAnalyzer(n_factors=n_factors, rotation="oblimin")
#     fa.fit(X)
#     loadings = pd.DataFrame(fa.loadings_, index=X.columns)

#     # Iterate over each variable (each row in the loadings dataframe)
#     for index, row in loadings.iterrows():
#         if all(abs(row) < threshold):  # If all factors for this variable have loadings below the threshold
#             low_loading_vars.append(index)

#     # Step 2: Remove the identified low-loading variables
#     X_filtered = X.drop(columns=low_loading_vars)

#     # Step 3: Re-run Factor Analysis with the filtered data
#     fa.fit(X_filtered)

# #    new_loadings = pd.DataFrame(fa.loadings_, index=X_filtered.columns)
    
#     variance_explained = fa.get_factor_variance()
#     print(f"\nVariance Explained per Factor:\n{variance_explained[1]}")  # Proportion per factor
#     print(f"Cumulative Variance Explained: {variance_explained[2][-1]:.2f}")  # Should be > 0.60
    
#     return X_filtered

# %% Import the dataset, specify the target variables

root_dir = "/Users/panosgtzouras/Desktop/datasets/csv/SUMsurveyData"

df = pd.read_csv(os.path.join(root_dir, "finalDatasets", "SumSurveyAssessV5.csv"))
df = df[df.city != "Geneva"]

# Extra changes in the dataset
df.loc[df['waitBus'] == 1014.5, 'waitBus'] = np.nan
df.loc[df['waitTrain'] == 1014.5, 'waitTrain'] = np.nan

df = fillAssessNans(df, df.columns)

df = relativeVars(df)

assessCols = ["afford",
#              "diffperSafeBike", "diffperSafeMoto", 
              "diffperSafePT", "diffperSafeTaxi", 
#              "diffperSafeWalk",
              "diffpsafeBike", "diffpsafeMoto", "diffpsafeWalk",
#              "diffpsafePT", "diffpsafeTaxi"
#              "reliable",
              "relpeakBike", 
              "relpeakMoto", 
#              "relpeakPT", 
              "relpeakTaxi", "relpeakWalk",
#      "relnonpeakBike", "relnonpeakMoto", "relnonpeakPT", "relnonpeakTaxi", "relnonpeakWalk",
                "waitBus", 
                "waitTrain",
              "walkBus", "walkTrain"]
pid = df['pid']


# %% Test for sample adequacy

# Bartlett’s test of sphericity
chi_square_value, p_value = calculate_bartlett_sphericity(df[assessCols])

print(f"Chi-square: {chi_square_value:.4f}")
print(f"P-value: {p_value:.4f}")

# if p_value < 0.05:
#     print("The correlation matrix is not an identity matrix — suitable for factor analysis.")
# else:
#     print("The correlation matrix is close to an identity matrix — not suitable for factor analysis.")

# KMO test
kmo_all, kmo_model = calculate_kmo(df[assessCols])

print("KMO for each variable:")
print(pd.Series(kmo_all, index=assessCols))
print("\nOverall KMO:", round(kmo_model, 3))

# %% Create the Scree plot to decide the number of factors

# Run factor analysis without rotation, get eigenvalues
fa = FactorAnalyzer(rotation=None)
fa.fit(df[assessCols])

eigen_values, vectors = fa.get_eigenvalues()

# Scree plot
plt.scatter(range(1, len(eigen_values)+1), eigen_values)
plt.plot(range(1, len(eigen_values)+1), eigen_values)
# plt.title('Scree Plot')
plt.xlabel('Factor')
plt.ylabel('Eigenvalue')
plt.grid()
plt.show()

total_vars = len(assessCols)
variance_explained = eigen_values / sum(eigen_values) * 100
cumulative_variance = variance_explained.cumsum()

for i, (ev, var, cum) in enumerate(zip(eigen_values, variance_explained, cumulative_variance), start=1):
     print(f"Factor {i}: eigenvalue={ev:.3f}, variance explained={var:.2f}%, cumulative={cum:.2f}%")

# %% Run the Factor Analysis

X = df[assessCols]
nf = 5

fa = FactorAnalyzer(n_factors = nf, rotation="oblimin")
fa.fit(X)
    
loadings = pd.DataFrame(fa.loadings_, index=X.columns)
print(loadings)

communalities = fa.get_communalities()
print(pd.Series(communalities, index=assessCols))
# %%

# for f in l.columns:  print(l.loc[abs(l[f]) > 0.10])

factor_scores = X.dot(fa.loadings_)
factor_scores.columns = [f"factor_{i+1}" for i in range(factor_scores.shape[1])]
factor_scores['pid'] = pid

df = pd.merge(df, factor_scores, on='pid', how='left')
    
# df.to_csv(os.path.join(root_dir, "finalDatasets", "SumSurveyAssessV8.csv"))

# %%
# Select only factor scores
factor_score_cols = [col for col in df.columns if col.startswith("factor_")]

# Compute correlation matrix
factor_score_corr = df[factor_score_cols].corr()

print("Correlation matrix of factor scores:")
print(factor_score_corr)