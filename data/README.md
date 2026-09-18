## Data source

**UCI Metro Interstate Traffic Volume dataset** — real hourly traffic
volume for I-94 westbound (Twin Cities, MN), with real weather
observations, Oct 2012–Sep 2018.

- Source: UCI Machine Learning Repository
  (https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume)
- Collected from MnDOT ATR station 301 (traffic) and OpenWeatherMap
  (weather), as documented by the original dataset contributors.
- `metro_traffic_raw.csv` is the full raw file (48,204 rows).
  `traffic_clean.csv` is the cleaned, feature-engineered version produced
  by `scripts/01_clean_and_feature_engineer.py`.
