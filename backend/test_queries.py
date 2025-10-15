import requests

BASE_URL = "http://127.0.0.1:5000/api"

def test_trips_endpoint():
    resp = requests.get(f"{BASE_URL}/trips?limit=5")
    assert resp.status_code == 200
    data = resp.json()
    assert "rows" in data
    print("Trips endpoint OK:", data["rows"][:2])

def test_summary_endpoint():
    resp = requests.get(f"{BASE_URL}/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_trips" in data
    print("Summary endpoint OK:", data)

def test_heatmap_endpoint():
    resp = requests.get(f"{BASE_URL}/heatmap")
    assert resp.status_code == 200
    data = resp.json()
    print("Heatmap endpoint OK, first cell:", data[0] if data else "No data")

if __name__ == "__main__":
    test_trips_endpoint()
    test_summary_endpoint()
    test_heatmap_endpoint()
