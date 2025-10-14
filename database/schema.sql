CREATE TABLE passengers (
    passenger_id INTEGER PRIMARY KEY AUTOINCREMENT,
    passenger_count INTEGER NOT NULL
);

CREATE TABLE trips (
    trip_id TEXT PRIMARY KEY,  
    vendor_id TEXT,
    pickup_datetime TEXT,
    dropoff_datetime TEXT,
    passenger_count INTEGER,       
    pickup_longitude REAL,
    pickup_latitude REAL,
    dropoff_longitude REAL,
    dropoff_latitude REAL,
    store_and_fwd_flag TEXT,
    passenger_id INTEGER,
    distance_km REAL,
    duration_min REAL,
    fare_amount REAL,
    tip_amount REAL,
    pickup_ts TEXT,
    dropoff_ts TEXT,
    pickup_lat REAL,
    pickup_lng REAL,
    dropoff_lat REAL,
    dropoff_lng REAL,
    FOREIGN KEY (passenger_id) REFERENCES passengers(passenger_id)
);

CREATE TABLE fares (
    fare_id INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_id TEXT,
    trip_duration INTEGER,
    trip_distance_km REAL,
    avg_speed_kmh REAL,
    FOREIGN KEY (trip_id) REFERENCES trips(trip_id)
);

CREATE INDEX idx_pickup_time ON trips (pickup_datetime);
CREATE INDEX idx_pickup_location ON trips (pickup_latitude, pickup_longitude);
