import sqlite3
import pandas as pd
from pathlib import Path

# File paths
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "taxi_data.db"
CSV_PATH = BASE_DIR.parent / "backend" / "data" / "train.csv"
SCHEMA_PATH = BASE_DIR.parent / "schema.sql"

def create_database():
    """Create database and apply schema.sql"""
    with sqlite3.connect(DB_PATH) as conn:
        with open(SCHEMA_PATH, "r") as f:
            conn.executescript(f.read())
    print("Database and schema created successfully.")

def load_data():
    """Load data from CSV into 3 tables."""
    df = pd.read_csv(CSV_PATH)

    with sqlite3.connect(DB_PATH) as conn:
        # Insert passengers
        passengers = pd.DataFrame(df["passenger_count"].unique(), columns=["passenger_count"])
        passengers.to_sql("passengers", conn, if_exists="append", index=False)

        # Insert trips
        trip_cols = [
            "tripid", "vendor_id", "pickup_datetime", "dropoff_datetime",
            "pickup_longitude", "pickup_latitude",
            "dropoff_longitude", "dropoff_latitude",
            "store_and_fwd_flag", "passenger_count"
        ]
        trips_df = df[trip_cols].rename(columns={"tripid": "trip_id"})
        trips_df.to_sql("trips", conn, if_exists="append", index=False)

        # Insert fares
        fares_df = pd.DataFrame({
            "trip_id": df["tripid"],
            "trip_duration": (pd.to_datetime(df["dropoff_datetime"]) - pd.to_datetime(df["pickup_datetime"])).dt.total_seconds(),
            "trip_distance_km": df["trip_distance"],
        })
        fares_df["avg_speed_kmh"] = fares_df["trip_distance_km"] / (fares_df["trip_duration"] / 3600)
        fares_df.to_sql("fares", conn, if_exists="append", index=False)

    print("All data inserted successfully.")

if __name__ == "__main__":
    create_database()
    load_data()
