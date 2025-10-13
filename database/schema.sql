-- Data from train.csv mapped into appropriate 3 tables in SQLITE

CREATE TABLE passengers (
    passenger_id INTEGER PRIMARY KEY AUTOINCREMENT,
    passenger_count INTEGER NOT NULL
);

CREATE TABLE trips (
    trip_id TEXT PRIMARY KEY,
    vendor_id TEXT,
    pickup_datetime DATETIME,
    dropoff_datetime DATETIME,
    pickup_longitude REAL,
    pickup_latitude REAL,
    dropoff_longitude REAL,
    dropoff_latitude REAL,
    store_and_fwd_flag INTEGER,
    passenger_id INTEGER,
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

-- Indexes for faster queries
CREATE INDEX idx_pickup_time ON trips (pickup_datetime);
CREATE INDEX idx_pickup_location ON trips (pickup_latitude, pickup_longitude);
