import sqlite3
from pathlib import Path

# Path to your database
DB_PATH = Path(__file__).parent / "taxi_data.db"

def run_query(query):
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(query).fetchall()
        for row in rows:
            print(row)

# Test basic queries
print("Trips (first 5):")
run_query("SELECT * FROM trips LIMIT 5;")

print("\nFares (first 5):")
run_query("SELECT * FROM fares LIMIT 5;")

print("\nPassengers (first 5):")
run_query("SELECT * FROM passengers LIMIT 5;")
