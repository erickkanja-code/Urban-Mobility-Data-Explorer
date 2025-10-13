from flask import Flask, jsonify, request
import sqlite3
from pathlib import Path

app = Flask(__name__)

# Build absolute path to the database
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR.parent / "database" / "taxi_data.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/trips', methods=['GET'])
def get_trips():
    conn = get_connection()
    cursor = conn.cursor()
    rows = cursor.execute("SELECT * FROM trips LIMIT 100").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

if __name__ == "__main__":
    app.run(debug=True)
