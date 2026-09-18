"""
Modeling: baseline Linear Regression -> Random Forest -> Gradient Boosting
Time-aware split (chronological, not random) since this is time-series data.
Includes lag-based temporal features that improve forecasting realism.
"""
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
MODELS_DIR = ROOT / "models"
MODELS_DIR.mkdir(exist_ok=True)


df = pd.read_csv(DATA_DIR / "traffic_clean.csv", parse_dates=["date_time"])
feature_cols = (DATA_DIR / "feature_columns.txt").read_text().splitlines()

X = df[feature_cols]
y = df["traffic_volume"]

split_idx = int(len(df) * 0.8)
X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
print(f"Train: {len(X_train)} rows ({df['date_time'].iloc[0]} to {df['date_time'].iloc[split_idx - 1]})")
print(f"Test:  {len(X_test)} rows ({df['date_time'].iloc[split_idx]} to {df['date_time'].iloc[-1]})")

models = {
    "Linear Regression (baseline)": LinearRegression(),
    "Random Forest": RandomForestRegressor(
        n_estimators=300,
        max_depth=18,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    ),
    "Gradient Boosting": GradientBoostingRegressor(
        n_estimators=250,
        learning_rate=0.05,
        max_depth=3,
        random_state=42,
    ),
}

results = {}
for name, model in models.items():
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    r2 = r2_score(y_test, preds)
    results[name] = {"MAE": mae, "RMSE": rmse, "R2": r2}
    print(f"\n{name}: MAE={mae:.1f}  RMSE={rmse:.1f}  R2={r2:.4f}")

best_name = max(results, key=lambda k: results[k]["R2"])
best_model = models[best_name]
print(f"\nBest model: {best_name}")

joblib.dump(best_model, MODELS_DIR / "best_model.pkl")
joblib.dump(feature_cols, MODELS_DIR / "feature_columns.pkl")

with open(MODELS_DIR / "metrics.json", "w") as f:
    json.dump({"results": results, "best_model": best_name}, f, indent=2)

if hasattr(best_model, "feature_importances_"):
    importances = pd.Series(best_model.feature_importances_, index=feature_cols).sort_values(ascending=False)
    print("\nTop 8 feature importances:\n", importances.head(8))
    importances.to_csv(MODELS_DIR / "feature_importances.csv")
