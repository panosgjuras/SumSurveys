import pandas as pd
import os
import googlemaps
import geopandas as gpd
from shapely.geometry import Point
from tqdm import tqdm
import numpy as np

root_dir = "/Users/panosgtzouras/Desktop/datasets/csv/SUMsurveyData"
GoogleMapKey = ""

gmaps = googlemaps.Client(key=GoogleMapKey)

location_points = pd.read_csv(os.path.join(root_dir, "finalDatasets", "locPointsUpd.csv"))

def createDiariesDf(df):
    for i in range(2, 6):
        df[f'orig{i}'] = df[f'dest{i-1}']

    dfs = []
    for i in range(1, 6):
        temp_df = df[[f'mode{i}', f'purp{i}', f'time{i}', f'orig{i}', f'dest{i}',
                      'pid','city']].rename(columns={f'mode{i}': 'mode', f'purp{i}': 'purp', f'time{i}': 'time',
                                                     f'orig{i}':'orig', f'dest{i}':'dest'})
        dfs.append(temp_df)

    cdf = pd.concat(dfs, ignore_index=True)

    cdf = cdf.dropna(subset=['mode', 'purp', 'time'])

    print(cdf.head())
    return (cdf)

def geocodeGoogle(addresses):
    results = []
    total_addresses = len(addresses)
    
    # Process each address and track progress
    for idx, address in enumerate(addresses):
        try:
            geocode_result = gmaps.geocode(address)  # Google Maps API call
            if geocode_result:
                # If geocoding is successful, store the coordinates (latitude, longitude)
                lat_lng = geocode_result[0]['geometry']['location']
                results.append((lat_lng['lat'], lat_lng['lng']))
            else:
                results.append(None)  # No result found
        except Exception as e:
            print(f"Error geocoding {address}: {e}")
            results.append(None)  # Error during geocoding
        
        # Calculate percentage of processed rows
        percentage_processed = ((idx + 1) / total_addresses) * 100
        print(f"Processing progress: {percentage_processed:.2f}% completed.")
    
    return results

def savelocPoints(df, coords_column, location_column, output_shp_path):
    valid_coords = df.dropna(subset=[coords_column])

    valid_coords[['latitude', 'longitude']] = pd.DataFrame(valid_coords[coords_column].to_list(), index=valid_coords.index)

    geometry = [Point(lon, lat) for lat, lon in zip(valid_coords['latitude'], valid_coords['longitude'])]

    gdf = gpd.GeoDataFrame(valid_coords, geometry=geometry)

    gdf.set_crs(epsg=4326, inplace=True)

    gdf_subset = gdf[['location','latitude', 'longitude', 'geometry']]  # Select only the desired columns

    gdf_subset.to_file(output_shp_path, driver='ESRI Shapefile')
    return gdf
    
def calculate_distance(orig_lat, orig_lon, dest_lat, dest_lon):
    """
    Calculate the distance between two points using Google Maps Distance Matrix API.
    
    Args:
    orig_lat (float): Latitude of the origin.
    orig_lon (float): Longitude of the origin.
    dest_lat (float): Latitude of the destination.
    dest_lon (float): Longitude of the destination.
    
    Returns:
    distance (str): Distance in kilometers or miles.
    """
    # Use the Google Maps Distance Matrix API
    origin = (orig_lat, orig_lon)
    destination = (dest_lat, dest_lon)
    
    # Get the distance
    result = gmaps.distance_matrix([origin], [destination], mode="driving")  # Mode can be "walking", "bicycling", etc.
    
    # Extract the distance from the API response
    try:
        distance = result['rows'][0]['elements'][0]['distance']['text']
        return distance
    except (IndexError, KeyError):
        return None  # In case of errors or no distance found

def convert_to_meters(distance_str):
    
    if distance_str == '1 m': distance_str = '5000 m'  # Replace '1 m' with '5000 m' (5 km)
    
    # Check if the distance_str is not None and is a string
    if distance_str and isinstance(distance_str, str):
        # Check if the string contains 'km' or 'm' and process accordingly
        if 'km' in distance_str:
            # Remove 'km' and convert to float, then multiply by 1000 to convert to meters
            return float(distance_str.replace(' km', ''))
        elif 'm' in distance_str:
            # Remove 'm' and convert to float
            return float(distance_str.replace(' m', ''))/1000
    return np.nan  # Return np.nan if the input is None or cannot be processed

def addTripDist(df, locPointsUpd2 = location_points):
    
    df["origC"] = df["orig"] + ", " + df["city"]
    df["destC"] = df["dest"] + ", " + df["city"]

    # locPoints = pd.DataFrame(pd.concat([df['origC'], df['destC']]).unique(), columns=['location'])
    # locPoints['coords'] = geocodeGoogle(locPoints['location']) 
    # savelocPoints(locPoints, 'coords', 'location', os.path.join(root_dir, 'locPointsCoords.shp'))

    # locPointsUpd = gpd.read_file(os.path.join(root_dir, 'locPointsCoordsUpd.shp'))
    # locPoints = locPoints[~locPoints['location'].isin(['An area within Jerusalem, Jerusalem', 'Another area in the country, Jerusalem',
    #                                                   'Nee, Rotterdam'])]
    # locPointsUpd['location2'] = locPoints["location"]
    # locPointsUpd.to_csv(os.path.join(root_dir, "locPointsUpd.csv"))
    
    
    # Merge for 'origC' and add suffix '_orig' for latitude and longitude columns
    df = df.merge(
        locPointsUpd2[['location2', 'latitude', 'longitude']], 
        left_on='origC', 
        right_on='location2', 
        how='left', 
        suffixes=('', '_orig')  # Add '_orig' to the new columns (latitude, longitude)
    )

    # Merge for 'destC' and add suffix '_dest' for latitude and longitude columns
    df = df.merge(
        locPointsUpd2[['location2', 'latitude', 'longitude']], 
        left_on='destC', 
        right_on='location2', 
        how='left', 
        suffixes=('', '_dest')  # Add '_dest' to the new columns (latitude, longitude)
    )

    df = df.drop(columns = ['Unnamed: 0','location2', 'origC', 'destC', 'orig_coords', 'location2_dest'])

    df.rename(columns={
        'latitude': 'orig_latitude',
        'longitude': 'orig_longitude',
        'latitude_dest': 'dest_latitude',
        'longitude_dest': 'dest_longitude'
    }, inplace=True)

    # Initialize tqdm with the DataFrame length
    tqdm.pandas(desc="Calculating distances")

    # Apply the function to your dataframe to calculate the distances for each row
    # This will also track progress and calculate the percentage of completion
    df['distance'] = df.progress_apply(lambda row: calculate_distance(row['orig_latitude'], row['orig_longitude'], row['dest_latitude'], row['dest_longitude']), axis=1)

    # Function to convert distance string to numeric value in meters

    # Apply the function to the 'distance' column
    df['fdistance'] = df['distance'].apply(convert_to_meters)

    # Replace NaN values with 5 km (5000 meters)
    df['fdistance'].fillna(5000, inplace=True)

    # df.to_csv(os.path.join(root_dir, 'SumSurveyDiariesV2.csv'))
    return df
    





