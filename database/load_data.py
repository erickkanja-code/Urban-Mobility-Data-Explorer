import sqlite3
import pandas as pd
from pathlib import Path

# Paths relative to this file
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "taxi_data.db"
CSV_PATH = BASE_DIR.parent / "backend" / "data" / "train.csv"
SCHEMA_PATH = BASE_DIR.parent / "schema.sql"

def create_database():
    """Create SQLite database and apply schema."""
    with sqlite3.connect(DB_PATH) as conn:
        with open(SCHEMA_PATH, "r") as f:
            conn.executescript(f.read())
    print("Database and schema created.")

def load_data():
    """Load CSV data into the 'trips' table using pandas."""
    df = pd.read_csv(CSV_PATH)

    with sqlite3.connect(DB_PATH) as conn:
        df.to_sql('trips', conn, if_exists='append', index=False)
    print(f"Inserted {len(df)} records into the database successfully.")

if __name__ == "__main__":
    create_database()
    load_data()
