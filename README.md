# g0ldf13h_web

Food & travel content site — landing page plus Food and Travel sections.

**Website:** [https://jinx-song.github.io/g0ldf13h_web/](https://jinx-song.github.io/g0ldf13h_web/)

## Restaurant map (Python)

The Food page map is driven by **Python**: the script `scripts/fetch_restaurants.py` fetches the [Goldfish restaurants spreadsheet](https://docs.google.com/spreadsheets/d/1-1samCRAdvP9G9tHhA3aOvJVfPgI6yLpfI6aRMigQzc/edit?gid=0#gid=0), geocodes each row, and writes `data/restaurants.json`. The site loads that JSON and plots markers with Leaflet.

