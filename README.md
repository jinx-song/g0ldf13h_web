# g0ldf13h_web

Food & travel content site — landing page plus Food and Travel sections.

**Website:** [https://jinx-song.github.io/g0ldf13h_web/](https://jinx-song.github.io/g0ldf13h_web/)

## Run locally

Open `index.html` in a browser, or serve the folder (e.g. `python3 -m http.server 8000`) and visit `http://localhost:8000`.

## Host on GitHub (use the repo as the domain)

The site is static and uses relative links, so it works on **GitHub Pages** at:

**`https://<your-username>.github.io/g0ldf13h_web/`**

1. Push this repo to GitHub (if you haven’t already).
2. In the repo on GitHub: **Settings → Pages**.
3. Under **Build and deployment**, set **Source** to **Deploy from a branch**.
4. Choose branch **main** (or your default branch) and folder **/ (root)**.
5. Click **Save**. After a minute or two, the site will be live at the URL above.

You can share that URL as the site’s “domain” (e.g. in your profile or links).

## Restaurant map (Python)

The Food page map is driven by **Python**: the script `scripts/fetch_restaurants.py` fetches the [Goldfish restaurants spreadsheet](https://docs.google.com/spreadsheets/d/1-1samCRAdvP9G9tHhA3aOvJVfPgI6yLpfI6aRMigQzc/edit?gid=0#gid=0), geocodes each row, and writes `data/restaurants.json`. The site loads that JSON and plots markers with Leaflet.

**Spreadsheet columns:** A = Name, B = Country, C = City, **D = Address**, E = Cuisine, F = Cuisine type, G = Average price. The script geocodes **Address** (column D) first for an exact pin; if missing or geocoding fails, it falls back to city/country.

- **Update the map manually:** from the repo root run  
  `python3 scripts/fetch_restaurants.py`  
  then commit and push `data/restaurants.json` if it changed.
- **Auto-update:** a GitHub Action runs every 6 hours and on pushes that touch the script or workflow; it regenerates `data/restaurants.json` and commits it when the spreadsheet has new or changed rows. New cities/addresses are geocoded via OpenStreetMap Nominatim (rate-limited). For the workflow to push commits, add a **Personal Access Token** as a repo secret: **Settings → Secrets and variables → Actions → New repository secret**, name it `GH_PAT`, and use a token with `repo` scope.
