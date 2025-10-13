import pandas as pd
import numpy as np
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(filename='logs/excluded_records.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(message)s')

# Load raw data
df = pd.read_csv('data/train.csv')

#  Step 1: Drop duplicates 
duplicates = df.duplicated().sum()
if duplicates > 0:
    logging.info(f"Dropped {duplicates} duplicate rows")
df = df.drop_duplicates()

# Step 2: Handle missing values 
missing_values = df.isnull().sum()
for col in df.columns:
    if df[col].isnull().sum() > 0:
        logging.info(f"Column '{col}' has {df[col].isnull().sum()} missing values")
df = df.dropna()  # or you can fillna depending on strategy

#  Step 3: Validate numeric fields 
# trip_duration should be >0, coordinates in NYC range
valid_trips = (df['trip_duration'] > 0) & \
              (df['pickup_latitude'].between(40.5, 41)) & \
              (df['dropoff_latitude'].between(40.5, 41)) & \
              (df['pickup_longitude'].between(-74.5, -73.5)) & \
              (df['dropoff_longitude'].between(-74.5, -73.5))

invalid_trips = df[~valid_trips]
for idx, row in invalid_trips.iterrows():
    logging.info(f"Excluded trip {row['id']} due to invalid coordinates or duration")
df = df[valid_trips]

#  Step 4: Normalize timestamps 
df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'])
df['dropoff_datetime'] = pd.to_datetime(df['dropoff_datetime'])

#  Step 5: Normalize categorical fields 
df['store_and_fwd_flag'] = df['store_and_fwd_flag'].map({'Y': 1, 'N': 0})

# Save cleaned dataset
df.to_csv('data/clean_trips.csv', index=False)
print("Data cleaned and saved to 'data/clean_trips.csv'")
