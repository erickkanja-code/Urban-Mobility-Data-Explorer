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
    df = pd.read_csv(CSV_PATH)

    with sqlite3.connect(DB_PATH) as conn:
        # Insert passengers
        passengers = pd.DataFrame(df["passenger_count"].unique(), columns=["passenger_count"])
        passengers.to_sql("passengers", conn, if_exists="append", index=False)

        # Insert trips (only columns that exist in the trips table)
        trips_cols = [
            "id", "vendor_id", "pickup_datetime", "dropoff_datetime",
            "passenger_count", "pickup_longitude", "pickup_latitude",
            "dropoff_longitude", "dropoff_latitude", "store_and_fwd_flag"
        ]
        trips_df = df[trips_cols].rename(columns={"id": "trip_id"})
        trips_df["trip_id"] = trips_df["trip_id"].astype(str)
        trips_df["vendor_id"] = trips_df["vendor_id"].astype(str)
        trips_df["store_and_fwd_flag"] = trips_df["store_and_fwd_flag"].astype(str)
        trips_df.to_sql("trips", conn, if_exists="append", index=False)

        # Insert fares (trip duration info)
        fares_df = pd.DataFrame({
            "trip_id": df["id"].astype(str),
            "trip_duration": df["trip_duration"],
            "trip_distance_km": None,
            "avg_speed_kmh": None
        })
        fares_df.to_sql("fares", conn, if_exists="append", index=False)

    print("All data inserted successfully.")

if __name__ == "__main__":
    create_database()
    load_data()
