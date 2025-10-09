import pandas as pd
import os

root_dir = "/Users/panosgtzouras/Desktop/datasets/csv/SUMsurveyData/finalDatasets"

df = pd.read_csv(os.path.join(root_dir, "SumSurveySocioV3.csv"))

df.head()
df.columns


import numpy as np
import pandas as pd

# Example: define your one-hot encoded age columns
age_columns = ['age_18_30', 'age_31_40', 'age_41_50', 'age_51_65', 'age_65_more']

# Define the numeric ranges for each age group
age_ranges = {
    'age_18_30': (18, 30),
    'age_31_40': (31, 40),
    'age_41_50': (41, 50),
    'age_51_65': (51, 65),
    'age_65_more': (66, 90)  # upper bound can be adjusted
}

# Function to generate a random age given a row
def random_age(row):
    for col in age_columns:
        if row[col] == 1:
            low, high = age_ranges[col]
            return np.random.randint(low, high + 1)
    return np.nan  # fallback if no group is active

# Apply to your DataFrame
df['age_int'] = df.apply(random_age, axis=1)

# Mean age per city
mean_age_per_city = df.groupby('city')['age_int'].mean().reset_index()

# Rename columns for clarity
mean_age_per_city.columns = ['city', 'mean_age']

print(mean_age_per_city)


df.groupby('city').count().reset_index()

