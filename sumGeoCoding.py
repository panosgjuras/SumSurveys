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

# %% Main functions

def sum_geocoding(df):
    
    df2 = df.copy()
    
    df2['orig2'] = df2['orig'].astype(str) + ", " + df['city']
    df2['dest2'] = df2['dest'].astype(str) + ", " + df['city']
    
    locations = pd.concat([df2['orig2'], df2['dest2']]).dropna().drop_duplicates()
    locations = pd.DataFrame({'location': locations})

    geolocator = Nominatim(user_agent="sum_living_labs_geocoder")
    
    geocode = RateLimiter(
        geolocator.geocode,
        min_delay_seconds=1,
        max_retries=3
    )
    
    locations['location'] = locations['location'].dropna()
    
    locations['geo'] = locations['location'].apply(geocode)
    
    locations['lat'] = locations['geo'].apply(lambda x: x.latitude if x else None)
    locations['lon'] = locations['geo'].apply(lambda x: x.longitude if x else None)
    
    return locations

def make_gpkg(locations, version):
    gdf = locations.dropna(subset=['lat', 'lon']).copy()
    gdf = gdf.drop(columns=['geo'], errors='ignore').copy()
    gdf['geometry'] = gdf.apply(
        lambda row: Point(row['lon'], row['lat']),
        axis=1)
    gdf = gpd.GeoDataFrame(gdf, geometry='geometry', crs="EPSG:4326")
    gdf.to_file(
        os.path.join(root_dir, f"geocoded_locations{version}.gpkg"),
        layer="locations",
        driver="GPKG")

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

def fill_manual_coords(row):
    if pd.isna(row['lat']) or pd.isna(row['lon']):
        coords = manual_coords.get(row['location'])
        if coords:
            return pd.Series([coords[0], coords[1]])
    return pd.Series([row['lat'], row['lon']])

def manual_coords_update(locations, updates):
    for loc, coords in updates.items():
        locations.loc[
            locations['location'] == loc,
            ['lat', 'lon']
        ] = coords
    return locations

# %% Automatic geolocation

df = pd.read_csv(os.path.join(root_dir, "SumSurveyDiariesV2.0.2.csv"))

locations = sum_geocoding(df) # DO NOT RUN IT AGAIN

version = "_v1"
make_gpkg(locations, version)

# %% Manual fixing of geolocations

# Rotterdam has no origin-destination points
# Larnaca has no origin-destination points
# Fredrikstad are completely missing, no survey

# find the coordinates of the failed points using Google Maps
failed = failed_geocode(locations)

manual_coords = {
 '610: Σπάτα, Ν. Μάκρη, Ραφήνα, Μαραθώνας, Athens' :(37.968191, 23.910175),
 '105: Σισμανόγλειο, Καμάρες, Athens' '100: Πεντέλη Βουνό, Athens' :(37.968191, 23.910175),
 '103: Βίγλα, Τερψιθέα, Athens': (38.06176776739204, 23.840848693994758),
 '106: Αμαλία Φλέμινγκ, 25ης Μαρτίου, Athens' : (38.054684149837534, 23.834869872239793),
 '107: Νεόκτιστα, Παλιαγιάννης, Σαλίγκαρος, Κακιά Σκάλα, Athens': (37.9838096, 23.7275388),
 '104: Αγ. Μαρίνα, Μαγερίνα, Athens': (38.05398172, 23.84568085),
 '605: Άλιμος, Γλυφάδα, Ηλιούπολη, Αργυρούπολη, Ελληνικό, Athens': (37.9168548, 23.7186146),
 '500: Αθήνα κέντρο, Athens': (37.9838096, 23.7275388),
 '609: Κορωπί, Μαρκόπουλο, Λαύριο, Ανάβυσσος, Athens': (37.8833564, 23.9333037),
 '606: Περιστέρι, Ίλιον, Αγ. Ανάργυροι, Athens': (0,0),
 '607: Ν. Ηράκλειο, Ν. Ιωνία, Ν. Φιλαδέλφεια, Γαλάτσι, Athens': (38.04065578623009, 23.768933209296243),
 '611: Αχαρνές, Αγ. Στέφανος, Διόνυσος, Ωρωπός, Athens': (37.9838096, 23.7275388),
 '602: Χαϊδάρι, Αιγάλεω, Κορυδαλλός, Νίκαια, Athens': (37.9845573, 23.6478153),
 '612: Φυλή, Ασπρόπυργος, Ελευσίνα, Μέγαρα, Athens': (37.9952107, 23.345307),
 '603: Καλλιθέα, Ταύρος, Μοσχάτο, Athens' : (37.95615269101097, 23.702723402732506),
 'Yuvalim Ganim, Jerusalem' : (31.753710248868394, 35.17049803998727),
 'Givat Masua, Jerusalem' : (31.750123194366456, 35.16821437727791),
 'Reches Lavan, Jerusalem' : (31.748979459517116, 35.15957622798716),
 'Bayit VeGan Ramat Sharet, Jerusalem' : (31.769680280199672, 35.184775797287294),
 "Ma'ar (CBD / City Center), Jerusalem" : (31.7810, 35.2196),
 'Rasco, Jerusalem' : (31.762678266641068, 35.20303049201401),
 'Givat Shaul Industrial Zone, Jerusalem': (31.792136635438947, 35.19488728824738),
 'Baka Moshavot, Jerusalem': (31.759258496743644, 35.2196601096048),
 "Nachlaot Sha'arei Chesed, Jerusalem": (31.78623005374961, 35.20878695030782),
 'Makor Baruch, Jerusalem': (31.789182244889705, 35.2119083298815),
 'Talpiot Industrial Zone, Jerusalem': (31.752380094402277, 35.21327810380562),
 'Gush Etzion, Jerusalem': (31.6690, 35.1215),
 'veyrier lancy bachet a pied, train a Berne retour, Geneva': (46.16605286752029, 6.178382570905729),
 'Bachet vers Rte de Veyrier, Geneva' : (46.17629292911239, 6.12393094313005),
# 'Pour aller et rentrer du travail, Geneva' : (0,0),
# "Départ de chez moi à vélo. 800m de trajet. Arrivée au bureau. Départ du bureau 900m de trajet. Arrivée au rdv. Départ du rdv jusqu'au magasin de vélo, 300m. Retour à pied chez moi, Geneva" : (0,0),
 'Genève centre à Genève centre (achats alimentaires), Geneva' : (46.20491348355323, 6.142859388818459),
# "je suis en déplacement à l'étranger. Dans la même commune j'ai dû marcher environ 45 min., Geneva" : (0,0),
# 'maison -> travail, travail -> maison, Geneva' : (0,0),
 'Je me suis rendue de mon logement à mon travail à vélo depuis Plan-les-Ouates., Geneva' : (46.166827077699566, 6.1136861414363475),
 'Leysin, Geneva' 'domicile à Nyon, Geneva' : (46.34576932688499, 7.013660918113015),
# 'Aproz (Nendaz/VS), Geneva' ,
 'Collonges Bellevue, Geneva' : (46.141695322415075, 6.144781879843948),
 'Vernie, Geneva' : (46.211506492011964, 6.1073468902625825),
# 'retour Bern Veyrier, Geneva' : (0,0),
# 'De mon domicile au centre commercial , Geneva' : (0,0),
 'Bois Ecard vers Place des Aviateurs, Geneva' : (46.16859694350549, 6.120347942356223),
# "Depuis mon travail jusqu'à un rdv. 900m à vélo, Geneva" : (0,0),
 'genève- arrêt acacias, Geneva' : (46.19282553719367, 6.13839261854068),
 'servette (travail UOG), Geneva' : (46.213647191668244, 6.129871208011474),
 'renens, Geneva' : (46.53378659954073, 6.591410304694897),
 'Gland, Geneva' : (46.42046614375563, 6.267261604121123), 
 'Wiedlisbach, Geneva' : (47.25118334826089, 7.645360572926388),
# 'La Givrine, Geneva'
 'St-Sulpice (VD), Geneva' : (46.51005327498263, 6.557789601499271),
# "Retour à pied car j'ai laissé mon vélo chez le réparateur, Geneva" : (0,0),
 'Portagem | Polo I (Universidade), Coimbra' : (40.20760775249469, -8.430180925341096),
 'S. Martinho | Santa Clara | Covões | Iparque, Coimbra' : (40.19421130396164, -8.451313025820557),
 'Umm al-Fahm, Jerusalem' : (32.517093772674436, 35.14831060354167),
 "Haredi Ma'ar, Jerusalem" : (31.7857, 35.2137),
 'Zichron Yaacov, Jerusalem':(31.79504094202089, 35.20123095344182),
 'Lutry, Geneva' : (46.50239079325718, 6.685561141311649),
# "J'ai été faire des courser et découvrir les rues environnantes de mon leu de résidence, Geneva" : (0,0),
 'genève -arrêt tram acacias, Geneva' : (46.19285522066536, 6.138371179820004),
 'Augustins (HUG), Geneva' : (46.19204938914605, 6.14378671365993),
# 'Le Brassus, col des Amburnex, Geneva' :(),
 'Nyon cebtre ville, Geneva' : (46.3833, 6.2390),
 'Ferney-Voltaire, Geneva' : (46.25800967312653, 6.109694532954785),
# 'emyrin, Geneva' : (0,0),
 'Nyon Migros Porte de Nyon, Geneva' : (46.38833654782171, 6.220671649136077)}
 
locations[['lat', 'lon']] = locations.apply(
    fill_manual_coords,
    axis=1
)
# version = "_v2"
# make_gpkg(locations, version)

# inspect the map and clean some wrong geolocated points
drop_locations = ["nan, Krakow", "nan, Jerusalem", "nan, Rotterdam"]
locations = locations[ ~locations['location'].isin(drop_locations)].copy()

# Give the locations, for which coordiations have to be updated
updates = {"The Old City, Jerusalem": (31.7767, 35.2345)} 
locations = manual_coords_update(locations, updates)

# save a new version and inspect again on GIS
version = "_v3"
make_gpkg(locations, version)
