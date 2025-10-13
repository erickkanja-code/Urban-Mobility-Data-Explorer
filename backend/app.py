# To run this Flask app, make sure Flask is installed:
# pip install flask
# Run with: python backend/app.py

from flask import Flask, jsonify, request
import sqlite3
from pathlib import Path

app = Flask(__name__)

# Path to database
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR.parent / "database" / "taxi_data.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

@app.route('/trips', methods=['GET'])
def get_trips():
    """Get first 100 trips"""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM trips LIMIT 100").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route('/trips/<trip_id>', methods=['GET'])
def get_trip_by_id(trip_id):
    """Get one trip by its trip_id"""
    conn = get_connection()
    row = conn.execute("SELECT * FROM trips WHERE trip_id = ?", (trip_id,)).fetchone()
    conn.close()
    if row:
        return jsonify(dict(row))
    else:
        return jsonify({"error": "Trip not found"}), 404

@app.route('/fares', methods=['GET'])
def get_fares():
    """Get first 100 fare records"""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM fares LIMIT 100").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

if __name__ == "__main__":
    app.run(debug=True)
@app.route('/trips/by_date', methods=['GET'])
def trips_by_date():
    """Filter trips by pickup date (YYYY-MM-DD)"""
    date = request.args.get("date")
    if not date:
        return jsonify({"error": "Please provide ?date=YYYY-MM-DD"}), 400

    conn = get_connection()
    query = """
        SELECT * FROM trips
        WHERE DATE(pickup_datetime) = ?
        LIMIT 100
    """
    rows = conn.execute(query, (date,)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@app.route('/trips/by_distance', methods=['GET'])
def trips_by_distance():
    """Filter fares by trip distance range"""
    min_d = float(request.args.get("min", 0))
    max_d = float(request.args.get("max", 10))

    conn = get_connection()
    query = """
        SELECT * FROM fares
        WHERE trip_distance_km BETWEEN ? AND ?
        LIMIT 100
    """
    rows = conn.execute(query, (min_d, max_d)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

if __name__ == "__main__":
    app.run(debug=True)
