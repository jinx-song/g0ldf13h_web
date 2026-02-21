#!/usr/bin/env python3
"""
Fetch restaurants from the Goldfish Google Sheet and build data/restaurants.json
for the food page map. Run this script to update the map data; it can be
scheduled (e.g. via GitHub Actions) to auto-update when the spreadsheet changes.
"""

import csv
import json
import os
import re
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
        if i == 0 and row and re.match(r"^(name|restaurant|title)$", (row[0] or "").strip(), re.I):
            continue
        name = (row[0] or "").strip()
        if not name:
            continue
        country = (row[1] or "").strip() if len(row) > 1 else ""
        city = (row[2] or "").strip() if len(row) > 2 else ""
        rows.append({"name": name, "country": country, "city": city})
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


def build_restaurants():
    csv_text = fetch_csv()
    rows = parse_csv(csv_text)
    out = []
    for r in rows:
        lat_lon = geocode_city(r["country"], r["city"])
        if lat_lon is None:
            continue
        out.append({
            "name": r["name"],
            "country": r["country"],
            "city": r["city"],
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
