#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  5 16:35:30 2026

@author: panosgtzouras
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter


# TODO: fix the pathing issue
root_dir = "/Users/panosgtzouras/Desktop/datasets/csv/SUMsurveyData/finalDatasets"
df = pd.read_csv(os.path.join(root_dir, "SumSurveyDiariesV2.0.2.csv"))

df['orig2'] = df['orig'].astype(str) + ", " + df['city']
df['dest2'] = df['dest'].astype(str) + ", " + df['city']

# unique locations
locations = pd.concat([df['orig2'], df['dest2']]).dropna().drop_duplicates()
locations = pd.DataFrame({'location': locations})


# geocoder
geolocator = Nominatim(user_agent="sum_living_labs_geocoder")

geocode = RateLimiter(
    geolocator.geocode,
    min_delay_seconds=1,
    max_retries=3
)

# add city/country context if useful

locations['location'] = locations['location'].dropna()

locations['geo'] = locations['location'].apply(geocode)

locations['lat'] = locations['geo'].apply(lambda x: x.latitude if x else None)
locations['lon'] = locations['geo'].apply(lambda x: x.longitude if x else None)

print(locations.head(10))

# %% Save locations

# TODO: make it a function with version and location as inputs to call it again and again
version = "_v1"

# Keep only valid coordinates
gdf = locations.dropna(subset=['lat', 'lon']).copy()
gdf = gdf.drop(columns=['geo'], errors='ignore').copy()

# Create geometry column
gdf['geometry'] = gdf.apply(
    lambda row: Point(row['lon'], row['lat']),
    axis=1
)

# Convert to GeoDataFrame (WGS84)
gdf = gpd.GeoDataFrame(gdf, geometry='geometry', crs="EPSG:4326")

# Save to GeoPackage
gdf.to_file(
    os.path.join(root_dir, f"geocoded_locations{version}.gpkg"),
    layer="locations",
    driver="GPKG"
)

# %% Manual fixing

# Rotterdam has no origin-destination points

# TODO: Import the gpkg with location, do not run again geolocation
# TODO: find the coordinates of the failed points using Google Maps
# TODO: inspect the map and clean some wrong geolocated points
# TODO: save a new version and inspect again on GIS

def failed_geocode(df):
    # Failed geocoding cases
    failed = df[df['lat'].isna() | df['lon'].isna()]
    # Print count
    print(f"Number of locations without coordinates: {len(failed)}")
    # Print the problematic addresses
    print("\nLocations not geocoded:")
    x = failed.location.unique()
    print(x)
    return x

failed = failed_geocode(locations)

manual_coords = {
    '610: Σπάτα, Ν. Μάκρη, Ραφήνα, Μαραθώνας, Athens': (37.968191, 23.910175),
    '105: Σισμανόγλειο, Καμάρες, Athens': (37.968191, 23.910175),
    
}

print(manual_coords)

def fill_manual_coords(row):
    if pd.isna(row['lat']) or pd.isna(row['lon']):
        coords = manual_coords.get(row['location'])
        if coords:
            return pd.Series([coords[0], coords[1]])
    return pd.Series([row['lat'], row['lon']])

locations[['lat', 'lon']] = locations.apply(
    fill_manual_coords,
    axis=1
)


