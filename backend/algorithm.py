"""
------------------------------------------------------------
Algorithm: Trip Ranking by Fare per km (Manual Selection Sort)
------------------------------------------------------------
Pseudo-code:
FUNCTION rank_trips(trips, top_n):
    FOR each trip t in trips:
        t.used = False
    top = []
    FOR n = 1 TO top_n:
        best_index = -1
        FOR i = 0 TO len(trips)-1:
            IF trips[i].used: CONTINUE
            IF best_index == -1 OR trips[i].fare_per_km > trips[best_index].fare_per_km:
                best_index = i
        IF best_index == -1: BREAK
        trips[best_index].used = True
        APPEND trips[best_index] TO top
    RETURN top
------------------------------------------------------------
Time Complexity: O(N × top_n)
Space Complexity: O(N)
------------------------------------------------------------
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "database" / "taxi_data.db"

def get_trips():
    """Fetch trips from the database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    q = """
        SELECT trip_id, fare_amount, distance_km
        FROM trips
        WHERE distance_km > 0 AND fare_amount IS NOT NULL
    """
    rows = conn.execute(q).fetchall()
    conn.close()
    trips = []
    for r in rows:
        trips.append({
            "trip_id": r["trip_id"],
            "fare_per_km": r["fare_amount"] / r["distance_km"]
        })
    return trips

def rank_trips(trips, top_n=10):
    """
    Manual selection of top N trips by fare_per_km (no built-in sort)
    Returns top N trips
    """
    # Mark all trips as unused
    for t in trips:
        t["used"] = False
    
    top = []
    for _ in range(top_n):
        best_index = -1
        for i in range(len(trips)):
            if trips[i]["used"]:
                continue
            if best_index == -1 or trips[i]["fare_per_km"] > trips[best_index]["fare_per_km"]:
                best_index = i
        if best_index == -1:
            break
        trips[best_index]["used"] = True
        top.append({
            "trip_id": trips[best_index]["trip_id"],
            "fare_per_km": trips[best_index]["fare_per_km"]
        })
    return top

if __name__ == "__main__":
    trips = get_trips()
    top_trips = rank_trips(trips, top_n=10)
    print("Top 10 Trips by Fare per km:")
    for t in top_trips:
        print(f"{t['trip_id']}: {t['fare_per_km']:.2f}")
