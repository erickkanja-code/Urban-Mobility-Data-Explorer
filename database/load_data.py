import sqlite3
import pandas as pd
from pathlib import Path

# File paths
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "taxi_data.db"
CSV_PATH = BASE_DIR.parent / "backend" / "data" / "train.csv"
SCHEMA_PATH = BASE_DIR / "schema.sql"

def create_database():
    """Create the database and apply schema."""
    with sqlite3.connect(DB_PATH) as conn:
        with open(SCHEMA_PATH, "r") as f:
            conn.executescript(f.read())
    print("Database and schema created successfully.")

def load_data():
    """Load data from train.csv into the database."""
    import math
    from datetime import datetime
    
    df = pd.read_csv(CSV_PATH)

    with sqlite3.connect(DB_PATH) as conn:
        # passengers
        passengers = pd.DataFrame(df["passenger_count"].unique(), columns=["passenger_count"])
        passengers.to_sql("passengers", conn, if_exists="replace", index=False)

        # calculate distance
        def get_distance(lat1, lon1, lat2, lon2):
            R = 6371
            lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            return R * c

        # calculate duration
        def get_duration(pickup, dropoff):
            try:
                start = datetime.strptime(pickup, '%Y-%m-%d %H:%M:%S')
                end = datetime.strptime(dropoff, '%Y-%m-%d %H:%M:%S')
                return (end - start).total_seconds() / 60
            except:
                return None

        # add missing columns
        df['distance_km'] = df.apply(lambda row: get_distance(
            row['pickup_latitude'], row['pickup_longitude'],
            row['dropoff_latitude'], row['dropoff_longitude']
        ), axis=1)
        
        df['duration_min'] = df.apply(lambda row: get_duration(
            row['pickup_datetime'], row['dropoff_datetime']
        ), axis=1)
        
        df['fare_amount'] = None
        df['tip_amount'] = None
        df['pickup_ts'] = df['pickup_datetime']
        df['dropoff_ts'] = df['dropoff_datetime']
        df['pickup_lat'] = df['pickup_latitude']
        df['pickup_lng'] = df['pickup_longitude']
        df['dropoff_lat'] = df['dropoff_latitude']
        df['dropoff_lng'] = df['dropoff_longitude']

        # trips table
        trips_cols = [
            "id", "vendor_id", "pickup_datetime", "dropoff_datetime",
            "passenger_count", "pickup_longitude", "pickup_latitude",
            "dropoff_longitude", "dropoff_latitude", "store_and_fwd_flag",
            "distance_km", "duration_min", "fare_amount", "tip_amount",
            "pickup_ts", "dropoff_ts", "pickup_lat", "pickup_lng", 
            "dropoff_lat", "dropoff_lng"
        ]
        trips_df = df[trips_cols].rename(columns={"id": "trip_id"})
        trips_df["trip_id"] = trips_df["trip_id"].astype(str)
        trips_df["vendor_id"] = trips_df["vendor_id"].astype(str)
        trips_df["store_and_fwd_flag"] = trips_df["store_and_fwd_flag"].astype(str)
        trips_df.to_sql("trips", conn, if_exists="replace", index=False)

        # fares table
        fares_df = pd.DataFrame({
            "trip_id": df["id"].astype(str),
            "trip_duration": df["trip_duration"],
            "trip_distance_km": df["distance_km"],
            "avg_speed_kmh": None
        })
        fares_df.to_sql("fares", conn, if_exists="replace", index=False)

    print("All data inserted successfully.")

if __name__ == "__main__":
    create_database()
    load_data()
