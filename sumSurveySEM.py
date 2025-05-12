import pandas as pd
import os
import numpy as np
import semopy
import matplotlib.pyplot as plt
import graphviz
import copy
from scipy.stats import norm

from sklearn.decomposition import PCA

from sklearn.preprocessing import StandardScaler

from factor_analyzer import FactorAnalyzer

from statsmodels.stats.outliers_influence import variance_inflation_factor

from sklearn.preprocessing import MinMaxScaler

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

def compare_frequencies(df_original, df_filled, cols_to_check):
    """
    Compares frequency distributions of specified columns before and after filling NaNs.

    Parameters:
    - df_original (pd.DataFrame): Original dataframe before NaN replacement
    - df_filled (pd.DataFrame): Updated dataframe after NaN replacement
    - cols_to_check (list): List of columns to analyze

    Returns:
    - dict: A dictionary with column names as keys and a DataFrame as values 
            showing frequency differences.
    """
    frequency_changes = {}

    for col in cols_to_check:
        # Compute relative frequency before filling NaNs
        freq_before = df_original[col].value_counts(normalize=True)
        freq_before.name = "Before"

        # Compute relative frequency after filling NaNs
        freq_after = df_filled[col].value_counts(normalize=True)
        freq_after.name = "After"

        # Combine into a DataFrame
        freq_comparison = pd.concat([freq_before, freq_after], axis=1).fillna(0)

        # Calculate absolute difference
        freq_comparison["Change"] = freq_comparison["After"] - freq_comparison["Before"]

        # Store result in dictionary
        frequency_changes[col] = freq_comparison

    return frequency_changes

def checkVIF(df, selected_vars):
    """
    Calculates the Variance Inflation Factor (VIF) for a selected set of variables.

    Parameters:
    - df (pd.DataFrame): The original dataframe.
    - selected_vars (list): List of column names to compute VIF for.

    Returns:
    - pd.DataFrame: DataFrame with variable names and their corresponding VIF values.
    """
    X = df[selected_vars]# Drop NaNs to avoid errors in VIF calculation
    vif_data = pd.DataFrame()
    vif_data["Variable"] = X.columns
    vif_data["VIF"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
    # print(vif_data)
    return vif_data

root_dir = "/Users/panosgtzouras/Desktop/datasets/csv/SUMsurveyData"
w = "finalDatasets"

assess = pd.read_csv(os.path.join(root_dir,w, "SumSurveyAssessV1.csv"))
assess = assess[assess.city != "Geneva"]

diaries = pd.read_csv(os.path.join(root_dir, w, "SumSurveyDiariesV1.csv"))
#diaries = diaries[diaries.city != "Geneva"]

# diaries = diaries.drop(columns = {"city"})
# df = pd.merge(assess, diaries, on ="pid", how = "left")
# df = df.dropna()
# exon = "car" + "_dist"
# assess = assess.merge(diaries.groupby("pid")[exon].sum().reset_index(), on="pid", how="left")

assessCols = [
    'afford', 'nonpeakCar', 'nonpeakTaxi', 'nonpeakPT', 'nonpeakMoto',
    'nonpeakBike', 'nonpeakWalk', 'peakCar', 'peakTaxi', 'peakPT',
    'peakMoto', 'peakBike', 'peakWalk', 'perSafeCar', 'perSafeTaxi',
    'perSafePT', 'perSafeMoto', 'perSafeBike', 'perSafeWalk', 'psafeCar',
    'psafeTaxi', 'psafePT', 'psafeMoto', 'psafeBike', 'psafeWalk', 
#    'reliable',
    'walkBus', 'walkTrain', 'waitBus', 'waitTrain'
]

df = copy.deepcopy(assess)
df = fillAssessNans(df, assessCols)

asModes = ["Taxi", "PT", "Moto", "Bike", "Walk"]
refmode = "Car"

for m in asModes:
    df["relnonpeak" + m] = df["nonpeak" + m]/df["nonpeak" + refmode]
    df["relpeak" + m] = df["peak" + m]/df["peak" + refmode]
    df["diffperSafe" + m] = df["perSafe" + m] - df["perSafe" + refmode]
    df["diffpsafe" + m] = df["psafe" + m] - df["psafe" + refmode]


checkVIF(df, ["relpeakTaxi","relnonpeakTaxi","diffperSafeTaxi","diffpsafeTaxi"])
checkVIF(df, ["relpeakPT", "relnonpeakPT", "walkBus", "walkTrain", "waitBus",
              "waitTrain", "diffperSafePT", "diffpsafePT"]) # STRONG VIF HERE
checkVIF(df, ["relpeakMoto", "relnonpeakMoto", "diffperSafeMoto", "diffpsafeMoto"])
checkVIF(df, ["relpeakBike", "relnonpeakBike", "diffperSafeBike", "diffpsafeBike"])
checkVIF(df, ["relpeakWalk", "relnonpeakWalk", "diffperSafeWalk", "diffpsafeWalk"])


# chekcVIF(df, [,"relpeakMoto","relpeakWalk"])

X = df[["relpeakTaxi","relnonpeakTaxi","diffperSafeTaxi","diffpsafeTaxi",
        "relpeakPT", "relnonpeakPT", "walkBus", "walkTrain", "waitBus",
        "waitTrain", "diffperSafePT", "diffpsafePT",
#       "reliable" 
        "relpeakMoto", "relnonpeakMoto", "diffperSafeMoto", "diffpsafeMoto",
        "relpeakBike", "relnonpeakBike", "diffperSafeBike", "diffpsafeBike",
        "relpeakWalk", "relnonpeakWalk", "diffperSafeWalk", "diffpsafeWalk"]]  # Replace with your observed variables

# X = df[assessCols]
pid = df['pid']

fa = FactorAnalyzer(n_factors = 5, rotation="oblimin")
fa.fit(X)

loadings = pd.DataFrame(fa.loadings_, index=X.columns)
print(loadings)

variance_explained = fa.get_factor_variance()

# Print results
print(f"Variance Explained per Factor:\n{variance_explained[1]}")  # Proportion per factor
print(f"Cumulative Variance Explained: {variance_explained[2][-1]:.2f}")  # Should be > 0.60

loadings = pd.DataFrame(fa.loadings_, index=X.columns)
print(loadings)

# df.to_csv(os.path.join(root_dir,w, "SumSurveyAssessV3.csv"))

def perfectFactorCombo(loadings, threshold = 0.3, n_factors=4):

    # Step 1: Identify variables to drop based on the threshold
    low_loading_vars = []

    # Calculate factor loadings using the FactorAnalyzer
    fa = FactorAnalyzer(n_factors=n_factors, rotation="oblimin")
    fa.fit(X)
    loadings = pd.DataFrame(fa.loadings_, index=X.columns)

    # Iterate over each variable (each row in the loadings dataframe)
    for index, row in loadings.iterrows():
        if all(abs(row) < threshold):  # If all factors for this variable have loadings below the threshold
            low_loading_vars.append(index)

    # Step 2: Remove the identified low-loading variables
    X_filtered = X.drop(columns=low_loading_vars)

    # Step 3: Re-run Factor Analysis with the filtered data
    fa.fit(X_filtered)

    # Step 4: Get the new factor loadings
    new_loadings = pd.DataFrame(fa.loadings_, index=X_filtered.columns)
    
    # Step 5: Get variance explained by the factors
    variance_explained = fa.get_factor_variance()

    # Print results
    # print(f"Updated Factor Loadings after Removal:")
    # print(new_loadings)

    # print(f"\nVariance Explained per Factor:\n{variance_explained[1]}")  # Proportion per factor
    # print(f"Cumulative Variance Explained: {variance_explained[2][-1]:.2f}")  # Should be > 0.60
    return



for f in range(2, 6):
    for t in np.arange(0.20, 0.70, 0.01):
        print(f"thereshold{t}, number of factors{f}")
        perfectFactorCombo(loadings, t, f)





def perfectFactorCombo(X, threshold=0.3, n_factors=4):

    fa = FactorAnalyzer(n_factors=n_factors, rotation="oblimin")
    fa.fit(X)

    variance_explained = fa.get_factor_variance()

    return variance_explained[2][-1]


results = []


for f in range(4, 10):  # For 2 to 5 factors
    for t in np.arange(0.20, 0.90, 0.01):  # For thresholds from 0.20 to 0.69
        print(f"Threshold: {t}, Number of Factors: {f}")
        
        # Perform the factor analysis and get the cumulative variance
        print(perfectFactorCombo(X, threshold=t, n_factors=f))








for f in loadings.columns:  print(loadings.loc[abs(loadings[f]) > 0.20])

factor_scores = X.dot(fa.loadings_)
factor_scores.columns = [f"factor_{i+1}" for i in range(factor_scores.shape[1])]
factor_scores['pid'] = pid

df = pd.merge(df, factor_scores, on='pid', how='left')




# Initialize PCA with the desired number of components (e.g., 6)
pca = PCA(n_components = 6)

# Fit PCA to the data and transform it
X_pca = pca.fit_transform(X)

# Check the explained variance ratio for each component
explained_variance = pca.explained_variance_ratio_
print(f"Explained Variance Ratio for each component: {explained_variance}")
cumulative_variance = np.cumsum(explained_variance)
print(f"Cumulative Variance Explained by PCA: {cumulative_variance[-1]:.2f}")

# Visualizing the explained variance (individual and cumulative)
plt.figure(figsize=(8, 6))

# Plot explained variance per component
plt.subplot(1, 2, 1)
plt.bar(range(1, len(explained_variance) + 1), explained_variance, alpha=0.7, color='blue')
plt.title("Explained Variance per Component")
plt.xlabel("Principal Component")
plt.ylabel("Explained Variance Ratio")
plt.xticks(range(1, len(explained_variance) + 1))

# Plot cumulative explained variance
plt.subplot(1, 2, 2)
plt.plot(range(1, len(cumulative_variance) + 1), cumulative_variance, marker='o', color='green')
plt.title("Cumulative Explained Variance")
plt.xlabel("Number of Components")
plt.ylabel("Cumulative Variance Explained")
plt.xticks(range(1, len(cumulative_variance) + 1))

# Show the plots
plt.tight_layout()
plt.show()

# Optionally, inspect the components
components_df = pd.DataFrame(pca.components_.T, index=X.columns, columns=[f"PC{i+1}" for i in range(pca.n_components_)])
print("\nPCA Components (Loadings):")
print(components_df)


component_scores_df = pd.DataFrame(X_pca, columns=[f'PC{i+1}' for i in range(X_pca.shape[1])])


for c in df.city.unique():
    print(c)


