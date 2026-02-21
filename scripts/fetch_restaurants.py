#!/usr/bin/env python3
"""
Fetch restaurants from the Goldfish Google Sheet and build data/restaurants.json
for the food page map. Run this script to update the map data; it can be
scheduled (e.g. via GitHub Actions) to auto-update when the spreadsheet changes.
"""

import csv
import json
import os
import time
from urllib.parse import quote
from urllib.request import Request, urlopen

SHEET_ID = "1-1samCRAdvP9G9tHhA3aOvJVfPgI6yLpfI6aRMigQzc"
SHEET_GID = "0"
CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={SHEET_GID}"
)

# Known city coordinates (no API calls). Add more as needed.
CITY_COORDS = {
    ("USA", "Seattle"): (47.6062, -122.3321),
    ("USA", "Boston"): (42.3601, -71.0589),
    ("USA", "Milwaukee"): (43.0389, -87.9065),
    ("USA", "Bellevue"): (47.6101, -122.2015),
}

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
OUTPUT_PATH = os.path.join(REPO_ROOT, "data", "restaurants.json")


def fetch_csv():
    req = Request(CSV_URL, headers={"User-Agent": "GoldfishWeb/1.0"})
    with urlopen(req) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_csv(csv_text):
    rows = []
    reader = csv.reader(csv_text.strip().splitlines())
    for i, row in enumerate(reader):
        if not row or not any(cell.strip() for cell in row):
            continue
        # Skip header-like first row
        first = (row[0] or "").strip().lower()
        if i == 0 and row and first in ("name", "restaurant", "title", "cuisine"):
            continue
        name = (row[0] or "").strip()
        if not name:
            continue
        country = (row[1] or "").strip() if len(row) > 1 else ""
        city = (row[2] or "").strip() if len(row) > 2 else ""
        address = (row[3] or "").strip() if len(row) > 3 else ""
        cuisine = (row[4] or "").strip() if len(row) > 4 else ""
        cuisine_type = (row[5] or "").strip() if len(row) > 5 else ""
        average_price = (row[6] or "").strip() if len(row) > 6 else ""
        rows.append({
            "name": name,
            "country": country,
            "city": city,
            "cuisine": cuisine,
            "cuisine_type": cuisine_type,
            "average_price": average_price,
            "address": address,
        })
    return rows


def geocode_city(country: str, city: str):
    key = (country or "", city or "")
    if key in CITY_COORDS:
        return CITY_COORDS[key]
    if not city and not country:
        return None
    query = ", ".join(filter(None, [city, country]))
    if not query:
        return None
    return _nominatim_geocode(query)


def _nominatim_geocode(query: str):
    try:
        url = (
            "https://nominatim.openstreetmap.org/search?"
            f"q={quote(query)}&format=json&limit=1"
        )
        req = Request(url, headers={"User-Agent": "GoldfishWeb/1.0 (food map)"})
        with urlopen(req) as resp:
            data = json.loads(resp.read().decode())
        if data and len(data) > 0:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            time.sleep(1)  # Nominatim rate limit
            return (lat, lon)
    except Exception:
        pass
    return None


def geocode_restaurant(row):
    """Geocode by full address (column D) for actual location; fallback to city/country."""
    address = (row.get("address") or "").strip()
    city = (row.get("city") or "").strip()
    country = (row.get("country") or "").strip()
    if address:
        # Build full query so Nominatim can resolve to actual location (e.g. "123 Main St, Seattle, USA")
        parts = [address]
        if city:
            parts.append(city)
        if country:
            parts.append(country)
        query = ", ".join(parts)
        coords = _nominatim_geocode(query)
        if coords:
            return coords
    return geocode_city(country, city)


def build_restaurants():
    csv_text = fetch_csv()
    rows = parse_csv(csv_text)
    out = []
    for r in rows:
        lat_lon = geocode_restaurant(r)
        if lat_lon is None:
            continue
        out.append({
            "name": r["name"],
            "country": r["country"],
            "city": r["city"],
            "cuisine": r.get("cuisine", ""),
            "cuisine_type": r.get("cuisine_type", ""),
            "average_price": r.get("average_price", ""),
            "address": r.get("address", ""),
            "lat": lat_lon[0],
            "lng": lat_lon[1],
        })
    return out


def main():
    restaurants = build_restaurants()
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(restaurants)} restaurants to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
