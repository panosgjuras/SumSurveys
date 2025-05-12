import pandas as pd
import os
import numpy as np

root_dir = os.path.dirname(os.path.realpath(__file__))
larnaca_data = pd.read_csv('setLarnaca.csv')

# Function to determine the value for the 'afford' column based on the criteria
def determine_afford(row):
    if row['afford10'] == 'Yes':
        return 0.5
    elif row['afford20'] == 'Yes':
        return 0.15
    elif row['afford30'] == 'Yes':
        return 0.25
    elif row['afford40'] == 'Yes':
        return 0.35
    elif row['afford50'] == 'Yes':
        return 0.45
    elif row['afford50plus'] == 'Yes':
        return 0.55
    else:
        return None

# Function to determine the value for the 'accept' and 'satisfy' columns based on the criteria
def determineReliableAcceptSatisfy(row, column_prefix):
    for i in range(1, 6):
        if row[f'{column_prefix}{i}'] == 'Yes':
            return i
    return None

def create_mode_columns(dataframe):
    """
    Function to create mode columns in a dataframe based on specific criteria.
    If a mode_type column (e.g., mode1_car) is 'Yes', then the corresponding mode column (mode1) is set to that mode_type.

    Args:
    dataframe (pd.DataFrame): The dataframe to modify.
    mode_prefixes (list): A list of mode prefixes (e.g., 'mode1', 'mode2', ...).
    mode_types (list): A list of mode types (e.g., 'car', 'taxi', 'bus', ...).

    Returns:
    pd.DataFrame: The modified dataframe with new mode columns.
    """
    
    mode_prefixes = ['mode1', 'mode2', 'mode3', 'mode4', 'mode5']
    mode_types = ['car', 'taxi', 'train', 'bus', 'motorcycle', 'bicycle', 
                  'escooter', 'walk', 'carsharing', 'micromobility', 'ridehailing']
    
    def determine_mode(row, mode_columns):
        for col in mode_columns:
            mode_type = col.split('_')[1]
            if row[col] == 'Yes':
                return mode_type
        return np.nan

    for prefix in mode_prefixes:
        mode_columns = [f'{prefix}_{mode_type}' for mode_type in mode_types if f'{prefix}_{mode_type}' in dataframe.columns]
        dataframe[prefix] = dataframe.apply(lambda row: determine_mode(row, mode_columns), axis=1)

    return dataframe


def create_purpose_columns(dataframe):
    """
    Function to create mode columns in a dataframe based on specific criteria.
    If a mode_type column (e.g., mode1_car) is 'Yes', then the corresponding mode column (mode1) is set to that mode_type.

    Args:
    dataframe (pd.DataFrame): The dataframe to modify.
    mode_prefixes (list): A list of mode prefixes (e.g., 'mode1', 'mode2', ...).
    mode_types (list): A list of mode types (e.g., 'car', 'taxi', 'bus', ...).

    Returns:
    pd.DataFrame: The modified dataframe with new mode columns.
    """
    
    mode_prefixes = ['purp1', 'purp2', 'purp3', 'purp4', 'purp5']
    mode_types = ['work', 'education', 'shopping', 'leisure', 'health', 
                    'services', 'other']
    
    def determine_mode(row, mode_columns):
        for col in mode_columns:
            mode_type = col.split('_')[1]
            if row[col] == 'Yes':
                return mode_type
        return np.nan

    for prefix in mode_prefixes:
        mode_columns = [f'{prefix}_{mode_type}' for mode_type in mode_types if f'{prefix}_{mode_type}' in dataframe.columns]
        dataframe[prefix] = dataframe.apply(lambda row: determine_mode(row, mode_columns), axis=1)

    return dataframe

def create_time_columns(dataframe):
    """
    Function to create time columns in a dataframe based on specific criteria.
    If a time_type column (e.g., time1_0800_1000) is 'Yes', then the corresponding time column (time1) is set to that time interval.

    Args:
    dataframe (pd.DataFrame): The dataframe to modify.

    Returns:
    pd.DataFrame: The modified dataframe with new time columns.
    """
    
    time_prefixes = ['time1', 'time2', 'time3', 'time4', 'time5']
    time_intervals = ['0508', '0811', '1114', '1417', '1720', '2023', '2324']
    
    def determine_time(row, time_columns):
        for col in time_columns:
            if row[col] == 'Yes':
                # Extracting time interval from the column name
                interval = col.split('_')[1]
                start_time = f"{interval[:2]}:00"
                end_time = f"{interval[2:]}:00"
                return f"{start_time}-{end_time}"
        return np.nan

    for prefix in time_prefixes:
        time_columns = [f'{prefix}_{interval}' for interval in time_intervals if f'{prefix}_{interval}' in dataframe.columns]
        dataframe[prefix] = dataframe.apply(lambda row: determine_time(row, time_columns), axis=1)

    return dataframe

def fixLarnaca(larnaca_data):
    # Afford fix
    larnaca_data['afford'] = larnaca_data.apply(determine_afford, axis=1)
    # Reliable fix
    larnaca_data['reliable'] = larnaca_data.apply(lambda row: determineReliableAcceptSatisfy(row, 'reliable'), axis=1)
    # Accept fix
    larnaca_data['accept'] = larnaca_data.apply(lambda row: determineReliableAcceptSatisfy(row, 'accept'), axis=1)
    # Satisfy fix
    larnaca_data['satisfy'] = larnaca_data.apply(lambda row: determineReliableAcceptSatisfy(row, 'satisfy'), axis=1)
    # Mode fix
    larnaca_data = create_mode_columns(larnaca_data)
    # Purp fix
    larnaca_data = create_purpose_columns(larnaca_data)
    # Time fix
    larnaca_data = create_time_columns(larnaca_data)
    
    return larnaca_data