import pandas as pd
from sumSurveyRenameSelect import callData, missCols, createDiariesDf
from sumSurveyReplacer import rePlacer, newAssessDF, genRandomTime
import geopandas as gpd
from scipy.spatial import distance_matrix


w = "finalBefore" # Before the implementation of measures

attr = ['mode1', 'time1', 'purp1', 'orig1', 'dest1',
        'mode2', 'time2', 'purp2', 'dest2',
        'mode3', 'time3', 'purp3', 'dest3',
        'mode4', 'time4', 'purp4', 'dest4',
        'mode5', 'time5', 'purp5', 'dest5'] # origin and destination dimmension is not yet considered

col = ['pid', 'city'] + attr
diaries = pd.DataFrame(columns = col)
c = 'Athens'
df = callData(c, when = w)[0]
df = missCols(df, attr)
diaries = pd.concat([diaries, df[col]],ignore_index=True)

diaries = createDiariesDf(diaries) 
diaries = rePlacer(diaries, 'mode') 
diaries = rePlacer(diaries, 'purp')
diaries['time'] =  diaries['time'].apply(genRandomTime)

shp_file_path = "/Users/panosgtzouras/Library/CloudStorage/GoogleDrive-panosgjuras@gmail.com/My Drive/PROJECTS_TZOURAS/SUM/live_Penteli/shapefiles/all_zones_final_SUMexp.shp"
zones =  gpd.read_file(shp_file_path)

center = zones.geometry.centroid

centroids = gpd.GeoDataFrame(zones.drop(columns='geometry'), geometry=center)

# Print the first few rows of the new GeoDataFrame
# print(centroids.head())

def createDistDf(centroids):
    coords = centroids.geometry.apply(lambda geom: (geom.x, geom.y)).tolist()
    dist_matrix = distance_matrix(coords, coords)
    dist_matrix = (1.3 * dist_matrix)/1000
    zone_codes = centroids['zoneCode']
    dist_df = pd.DataFrame(dist_matrix, index=zone_codes, columns=zone_codes)
    return dist_df
    
distDf = createDistDf(centroids)

def get_distance(orig_zone, dest_zone):
    try:
        return distDf.at[orig_zone, dest_zone]
    except KeyError:
        return None

def findTripDistances(df):
    df['orig_zone'] = df['orig'].apply(lambda x: x.split(':')[0].strip())
    df['dest_zone'] = df['dest'].apply(lambda x: x.split(':')[0].strip())

    # Convert to integer for easier matching
    df['orig_zone'] = df['orig_zone'].astype(int)
    df['dest_zone'] = df['dest_zone'].astype(int)

    df['distance'] = df.apply(lambda row: get_distance(row['orig_zone'], 
                                    row['dest_zone']), axis=1)
    df = df.drop(columns = ['orig_zone', 'dest_zone'])
    return df

diaries = findTripDistances(diaries)

def calculateDistancePerMode(df):
    """
    Calculate total distance traveled per transport mode.
    """
    # Group by transport mode and sum the distances
    mode_distances = df.groupby('mode')['distance'].sum()
    
    return mode_distances

# Calculate the total distance per transport mode
distance_per_mode = calculateDistancePerMode(diaries)
pop = 35610
resp = 210
print(pop * distance_per_mode/resp)

diaries.groupby('mode').count()




