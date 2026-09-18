"""
Data Preparation & Feature Engineering
Metro Interstate Traffic Volume dataset (UCI) -> cleaned, feature-engineered dataset
Adds lag-based temporal features for stronger forecasting performance.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_PATH = DATA_DIR / "metro_traffic_raw.csv"
OUTPUT_PATH = DATA_DIR / "traffic_clean.csv"
FEATURES_PATH = DATA_DIR / "feature_columns.txt"


def add_lag_features(df: pd.DataFrame, lag_hours=(1, 3, 24), rolling_window=3):
    for lag in lag_hours:
        df[f"traffic_volume_lag_{lag}h"] = df["traffic_volume"].shift(lag)

    df[f"rolling_{rolling_window}h_mean"] = (
        df["traffic_volume"].shift(1).rolling(window=rolling_window, min_periods=1).mean()
    )
    return df


df = pd.read_csv(RAW_PATH)
print(f"Raw rows: {len(df)}")

before = len(df)
df = df.drop_duplicates(subset=["date_time"], keep="first")
print(f"Dropped {before - len(df)} duplicate timestamp rows -> {len(df)} rows")

before = len(df)
df = df[df["temp"] > 0]
print(f"Dropped {before - len(df)} rows with temp=0K sensor error -> {len(df)} rows")

df["date_time"] = pd.to_datetime(df["date_time"])
df["is_holiday"] = df["holiday"].notna().astype(int)

df["hour"] = df["date_time"].dt.hour
df["day_of_week"] = df["date_time"].dt.dayofweek
df["month"] = df["date_time"].dt.month
df["year"] = df["date_time"].dt.year
df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
df["dow_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
df["dow_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)

df["temp_c"] = df["temp"] - 273.15

weather_dummies = pd.get_dummies(df["weather_main"], prefix="weather", dtype=int)
df = pd.concat([df, weather_dummies], axis=1)
df = add_lag_features(df)

df = df.sort_values("date_time").reset_index(drop=True)

for col in ["traffic_volume_lag_1h", "traffic_volume_lag_3h", "traffic_volume_lag_24h", "rolling_3h_mean"]:
    df[col] = df[col].fillna(0)

feature_cols = (
    [
        "temp_c",
        "rain_1h",
        "snow_1h",
        "clouds_all",
        "is_holiday",
        "hour_sin",
        "hour_cos",
        "dow_sin",
        "dow_cos",
        "is_weekend",
        "month",
        "traffic_volume_lag_1h",
        "traffic_volume_lag_3h",
        "traffic_volume_lag_24h",
        "rolling_3h_mean",
    ]
    + list(weather_dummies.columns)
)

df.to_csv(OUTPUT_PATH, index=False)
print(f"\nFinal clean dataset: {len(df)} rows, {len(feature_cols)} features")
print(f"Date range: {df['date_time'].min()} to {df['date_time'].max()}")
with open(FEATURES_PATH, "w") as f:
    f.write("\n".join(feature_cols))
