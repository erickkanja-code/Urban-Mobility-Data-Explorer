import sqlite3
import pandas as pd
from pathlib import Path

# File paths
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "taxi_data.db"
CSV_PATH = BASE_DIR.parent / "backend" / "data" / "clean_trips_features.csv"
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

        # Use pre-calculated fields from features.py
        # distance_km and duration_min are already calculated in clean_trips_features.csv
        
        df['fare_amount'] = None
        df['tip_amount'] = None
        df['pickup_ts'] = df['pickup_datetime']
        df['dropoff_ts'] = df['dropoff_datetime']
        df['pickup_lat'] = df['pickup_latitude']
        df['pickup_lng'] = df['pickup_longitude']
        df['dropoff_lat'] = df['dropoff_latitude']
        df['dropoff_lng'] = df['dropoff_longitude']

        # trips table - match schema exactly
        trips_df = pd.DataFrame({
            "trip_id": df["id"].astype(str),
            "vendor_id": df["vendor_id"].astype(str) if "vendor_id" in df.columns else "1",
            "pickup_datetime": df["pickup_datetime"].astype(str),
            "dropoff_datetime": df["dropoff_datetime"].astype(str),
            "passenger_count": df["passenger_count"],
            "pickup_longitude": df["pickup_longitude"],
            "pickup_latitude": df["pickup_latitude"],
            "dropoff_longitude": df["dropoff_longitude"],
            "dropoff_latitude": df["dropoff_latitude"],
            "store_and_fwd_flag": df["store_and_fwd_flag"].astype(str),
            "passenger_id": None,  # Will be set later
            "distance_km": df["trip_distance_km"],
            "duration_min": df["trip_duration"] / 60,  # Convert seconds to minutes
            "fare_amount": df["fare_amount"],
            "tip_amount": df["tip_amount"],
            "pickup_ts": df["pickup_datetime"],
            "dropoff_ts": df["dropoff_datetime"],
            "pickup_lat": df["pickup_latitude"],
            "pickup_lng": df["pickup_longitude"],
            "dropoff_lat": df["dropoff_latitude"],
            "dropoff_lng": df["dropoff_longitude"]
        })
        trips_df.to_sql("trips", conn, if_exists="replace", index=False)

        # fares table - match schema exactly
        fares_df = pd.DataFrame({
            "trip_id": df["id"].astype(str),
            "trip_duration": df["trip_duration"],
            "trip_distance_km": df["trip_distance_km"],
            "avg_speed_kmh": df["avg_speed_kmh"]
        })
        fares_df.to_sql("fares", conn, if_exists="replace", index=False)

    print("All data inserted successfully.")

if __name__ == "__main__":
    create_database()
    load_data()
