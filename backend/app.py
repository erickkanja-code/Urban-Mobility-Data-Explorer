# backend/app.py
# To run: pip install flask flask-cors
# Run with: python backend/app.py

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from pathlib import Path
from math import floor

app = Flask(__name__)
CORS(app)

# Path to database (assumes database/taxi_data.db exists relative to project root)
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR.parent / "database" / "taxi_data.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    return conn

def row_to_dict(row):
    if row is None:
        return None
    d = dict(row)
    # Convert bytes/None to plain types and ensure numeric casts for JSON
    for k,v in d.items():
        if isinstance(v, bytes):
            try:
                d[k] = v.decode('utf-8')
            except Exception:
                d[k] = str(v)
        # attempt conversions for common numeric fields
        if v is None:
            d[k] = None
        else:
            if k in ("fare_amount","tip_amount","distance_km","duration_min"):
                try:
                    d[k] = float(v)
                except Exception:
                    pass
    return d

@app.route("/api/trips", methods=["GET"])
def api_get_trips():
    """
    GET /api/trips?start=YYYY-MM-DD&end=YYYY-MM-DD&min_distance=&limit=&page=
    Returns JSON: { rows: [...], total: N }
    """
    start = request.args.get("start")
    end = request.args.get("end")
    min_distance = request.args.get("min_distance")
    try:
        limit = int(request.args.get("limit", 20))
    except:
        limit = 20
    try:
        page = int(request.args.get("page", 1))
    except:
        page = 1
    offset = (page - 1) * limit

    where_clauses = []
    params = []

    if start:
        where_clauses.append("DATE(pickup_datetime) >= DATE(?)")
        params.append(start)
    if end:
        where_clauses.append("DATE(pickup_datetime) <= DATE(?)")
        params.append(end)
    if min_distance:
        # assume distance_km column exists (derived during ingest)
        where_clauses.append("distance_km >= ?")
        try:
            params.append(float(min_distance))
        except:
            params.append(0)

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    conn = get_connection()

    # total count for pagination
    total_q = f"SELECT COUNT(*) as cnt FROM trips {where_sql}"
    total_row = conn.execute(total_q, params).fetchone()
    total = total_row["cnt"] if total_row else 0

    q = f"""
        SELECT trip_id as id,
               pickup_datetime as pickup_ts,
               dropoff_datetime as dropoff_ts,
               pickup_lat, pickup_lng,
               dropoff_lat, dropoff_lng,
               fare_amount, tip_amount,
               distance_km, duration_min,
               passenger_count
        FROM trips
        {where_sql}
        LIMIT ? OFFSET ?
    """
    exec_params = params + [limit, offset]
    rows = conn.execute(q, exec_params).fetchall()
    conn.close()

    rows_list = [row_to_dict(r) for r in rows]
    return jsonify({"rows": rows_list, "total": total})

@app.route("/api/trip/<int:trip_id>", methods=["GET"])
def api_get_trip(trip_id):
    conn = get_connection()
    q = """
      SELECT *
      FROM trips
      WHERE trip_id = ?
      LIMIT 1
    """
    row = conn.execute(q, (trip_id,)).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Trip not found"}), 404
    return jsonify(row_to_dict(row))

@app.route("/api/summary", methods=["GET"])
def api_summary():
    """
    /api/summary?start=YYYY-MM-DD&end=YYYY-MM-DD
    Returns:
    {
      total_trips: int,
      avg_distance_km: float,
      avg_duration_min: float,
      total_revenue: float,
      trips_per_hour: [{hour: "00", count: 123}, ...]
    }
    """
    start = request.args.get("start")
    end = request.args.get("end")

    where_clauses = []
    params = []
    if start:
        where_clauses.append("DATE(pickup_datetime) >= DATE(?)")
        params.append(start)
    if end:
        where_clauses.append("DATE(pickup_datetime) <= DATE(?)")
        params.append(end)
    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    conn = get_connection()

    # aggregated metrics
    q_agg = f"""
      SELECT
        COUNT(*) as total_trips,
        AVG(distance_km) as avg_distance_km,
        AVG(duration_min) as avg_duration_min,
        SUM(COALESCE(fare_amount,0) + COALESCE(tip_amount,0)) as total_revenue
      FROM trips
      {where_sql}
    """
    agg = conn.execute(q_agg, params).fetchone()

    # trips per hour
    # use strftime('%H', pickup_datetime) for hour
    q_hour = f"""
      SELECT strftime('%H', pickup_datetime) as hour, COUNT(*) as cnt
      FROM trips
      {where_sql}
      GROUP BY hour
      ORDER BY hour
    """
    hour_rows = conn.execute(q_hour, params).fetchall()
    conn.close()

    trips_per_hour = []
    for hr in hour_rows:
        trips_per_hour.append({"hour": hr["hour"], "count": hr["cnt"]})

    resp = {
        "total_trips": int(agg["total_trips"]) if agg and agg["total_trips"] is not None else 0,
        "avg_distance_km": float(agg["avg_distance_km"]) if agg and agg["avg_distance_km"] is not None else 0.0,
        "avg_duration_min": float(agg["avg_duration_min"]) if agg and agg["avg_duration_min"] is not None else 0.0,
        "total_revenue": float(agg["total_revenue"]) if agg and agg["total_revenue"] is not None else 0.0,
        "trips_per_hour": trips_per_hour
    }
    return jsonify(resp)

@app.route("/api/heatmap", methods=["GET"])
def api_heatmap():
    """
    /api/heatmap?start=&end=&grid_size=0.01
    Returns aggregated pickup counts per grid cell: [{lat, lng, count}, ...]
    """
    start = request.args.get("start")
    end = request.args.get("end")
    try:
        grid_size = float(request.args.get("grid_size", 0.01))
    except:
        grid_size = 0.01

    where_clauses = []
    params = []
    if start:
        where_clauses.append("DATE(pickup_datetime) >= DATE(?)")
        params.append(start)
    if end:
        where_clauses.append("DATE(pickup_datetime) <= DATE(?)")
        params.append(end)
    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    conn = get_connection()
    # fetch pickup coords only (limit to reasonable number for web demo)
    q = f"""
      SELECT pickup_lat, pickup_lng
      FROM trips
      {where_sql}
      WHERE pickup_lat IS NOT NULL AND pickup_lng IS NOT NULL
      LIMIT 50000
    """
    try:
        rows = conn.execute(q, params).fetchall()
    except Exception:
        # fallback if WHERE duplication occurs
        q = f"SELECT pickup_lat, pickup_lng FROM trips WHERE pickup_lat IS NOT NULL AND pickup_lng IS NOT NULL LIMIT 50000"
        rows = conn.execute(q).fetchall()
    conn.close()

    # aggregate to grid cells (manual)
    counts = {}
    for r in rows:
        lat = r["pickup_lat"]
        lng = r["pickup_lng"]
        try:
            latf = float(lat); lngf = float(lng)
        except Exception:
            continue
        lat_idx = int(floor(latf / grid_size))
        lng_idx = int(floor(lngf / grid_size))
        key = f"{lat_idx}|{lng_idx}"
        counts[key] = counts.get(key, 0) + 1

    cells = []
    for key, cnt in counts.items():
        lat_idx, lng_idx = key.split("|")
        latc = (int(lat_idx) + 0.5) * grid_size
        lngc = (int(lng_idx) + 0.5) * grid_size
        cells.append({"lat": latc, "lng": lngc, "count": cnt})

    # Optionally reduce number of cells by returning top N by count (manual selection)
    # We'll return all cells; frontend scales marker radius by count
    return jsonify(cells)

# Manual top-N selection: returns top N grid cells from DB (server-side)
@app.route("/api/top-zones", methods=["GET"])
def api_top_zones():
    """
    /api/top-zones?start=&end=&grid_size=0.01&n=10
    Returns top N busiest pickup grid cells using manual selection (no sorted())
    """
    start = request.args.get("start")
    end = request.args.get("end")
    try:
        grid_size = float(request.args.get("grid_size", 0.01))
    except:
        grid_size = 0.01
    try:
        N = int(request.args.get("n", 10))
    except:
        N = 10

    where_clauses = []
    params = []
    if start:
        where_clauses.append("DATE(pickup_datetime) >= DATE(?)")
        params.append(start)
    if end:
        where_clauses.append("DATE(pickup_datetime) <= DATE(?)")
        params.append(end)
    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    conn = get_connection()
    q = f"""
      SELECT pickup_lat, pickup_lng
      FROM trips
      {where_sql}
      WHERE pickup_lat IS NOT NULL AND pickup_lng IS NOT NULL
      LIMIT 50000
    """
    try:
        rows = conn.execute(q, params).fetchall()
    except Exception:
        q = "SELECT pickup_lat, pickup_lng FROM trips WHERE pickup_lat IS NOT NULL AND pickup_lng IS NOT NULL LIMIT 50000"
        rows = conn.execute(q).fetchall()
    conn.close()

    # aggregate
    counts = {}
    for r in rows:
        try:
            latf = float(r["pickup_lat"]); lngf = float(r["pickup_lng"])
        except Exception:
            continue
        lat_idx = int(floor(latf / grid_size))
        lng_idx = int(floor(lngf / grid_size))
        key = f"{lat_idx}|{lng_idx}"
        counts[key] = counts.get(key, 0) + 1

    arr = []
    for key, cnt in counts.items():
        lat_idx, lng_idx = key.split("|")
        arr.append({
            "key": key,
            "count": cnt,
            "lat": (int(lat_idx) + 0.5) * grid_size,
            "lng": (int(lng_idx) + 0.5) * grid_size,
            "used": False
        })

    # manual top-N (no sort)
    top = []
    for _ in range(N):
        best = -1
        for i in range(len(arr)):
            if arr[i]["used"]:
                continue
            if best == -1 or arr[i]["count"] > arr[best]["count"]:
                best = i
        if best == -1:
            break
        arr[best]["used"] = True
        top.append({k: arr[best][k] for k in ("lat","lng","count")})

    return jsonify(top)

if __name__ == "__main__":
    # Run dev server
    app.run(host="0.0.0.0", port=5000, debug=True)
