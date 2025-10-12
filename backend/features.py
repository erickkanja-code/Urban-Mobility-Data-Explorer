import pandas as pd
import numpy as np
from math import radians, cos, sin, asin, sqrt

# Load cleaned data
df = pd.read_csv('data/clean_trips.csv')

# --- Feature 1: Trip distance (Haversine formula) ---
def haversine(lon1, lat1, lon2, lat2):
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371  # Radius of Earth in km
    return c * r

df['trip_distance_km'] = df.apply(lambda x: haversine(
    x['pickup_longitude'], x['pickup_latitude'],
    x['dropoff_longitude'], x['dropoff_latitude']), axis=1)

# --- Feature 2: Average speed (km/h) ---
df['trip_duration_h'] = df['trip_duration'] / 3600  # seconds -> hours
df['avg_speed_kmh'] = df['trip_distance_km'] / df['trip_duration_h']
df.loc[df['trip_duration_h'] == 0, 'avg_speed_kmh'] = 0  # handle divide by zero

# --- Feature 3: Trip hour of day ---
df['pickup_hour'] = pd.to_datetime(df['pickup_datetime']).dt.hour

# Save enhanced dataset
df.to_csv('data/clean_trips_features.csv', index=False)
print("Features engineered and saved to 'data/clean_trips_features.csv'")
