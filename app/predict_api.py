"""FastAPI service for traffic volume prediction.

Run locally:
    uvicorn app.predict_api:app --host 0.0.0.0 --port 8000 --reload
"""
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "best_model.pkl"
FEATURES_PATH = ROOT / "models" / "feature_columns.pkl"


class PredictionRequest(BaseModel):
    hour: int = Field(..., ge=0, le=23)
    day_of_week: int = Field(..., ge=0, le=6)
    month: int = Field(default=6, ge=1, le=12)
    temp_c: float = 15.0
    rain_1h: float = 0.0
    snow_1h: float = 0.0
    clouds_all: int = Field(default=0, ge=0, le=100)
    is_holiday: int = Field(default=0, ge=0, le=1)
    weather_main: str = "Clear"
    traffic_volume_lag_1h: float = 0.0
    traffic_volume_lag_3h: float = 0.0
    traffic_volume_lag_24h: float = 0.0
    rolling_3h_mean: float = 0.0


class BatchPredictionRequest(BaseModel):
    items: list[PredictionRequest]


app = FastAPI(title="Traffic Flow Predictor", version="1.1.0")
model = joblib.load(MODEL_PATH)
feature_cols = joblib.load(FEATURES_PATH)
weather_categories = [c.replace("weather_", "") for c in feature_cols if c.startswith("weather_")]


def build_feature_row(payload: dict):
    payload = dict(payload)
    hour = int(payload["hour"])
    dow = int(payload["day_of_week"])
    row = {
        "temp_c": float(payload.get("temp_c", 15.0)),
        "rain_1h": float(payload.get("rain_1h", 0.0)),
        "snow_1h": float(payload.get("snow_1h", 0.0)),
        "clouds_all": float(payload.get("clouds_all", 0)),
        "is_holiday": int(payload.get("is_holiday", 0)),
        "hour_sin": np.sin(2 * np.pi * hour / 24),
        "hour_cos": np.cos(2 * np.pi * hour / 24),
        "dow_sin": np.sin(2 * np.pi * dow / 7),
        "dow_cos": np.cos(2 * np.pi * dow / 7),
        "is_weekend": int(dow >= 5),
        "month": int(payload.get("month", 6)),
        "traffic_volume_lag_1h": float(payload.get("traffic_volume_lag_1h", 0.0)),
        "traffic_volume_lag_3h": float(payload.get("traffic_volume_lag_3h", 0.0)),
        "traffic_volume_lag_24h": float(payload.get("traffic_volume_lag_24h", 0.0)),
        "rolling_3h_mean": float(payload.get("rolling_3h_mean", 0.0)),
    }

    weather = payload.get("weather_main", "Clear")
    for w in weather_categories:
        row[f"weather_{w}"] = 1 if w == weather else 0

    missing = [c for c in feature_cols if c not in row]
    for col in missing:
        row[col] = 0.0

    return pd.DataFrame([row])[feature_cols]


def prediction_summary(X: pd.DataFrame) -> dict:
    prediction = float(model.predict(X)[0])

    if hasattr(model, "estimators_"):
        values = X.to_numpy()
        tree_predictions = np.array([tree.predict(values)[0] for tree in model.estimators_], dtype=float)
        lower = float(np.percentile(tree_predictions, 10))
        upper = float(np.percentile(tree_predictions, 90))
        method = "10th-90th percentile across Random Forest trees"
    else:
        lower = max(0.0, prediction - 300.0)
        upper = prediction + 300.0
        method = "fallback +/- 300 vehicles/hour"

    return {
        "predicted_traffic_volume": round(prediction, 1),
        "prediction_interval": {
            "lower": round(max(0.0, lower), 1),
            "upper": round(max(0.0, upper), 1),
            "method": method,
        },
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/metadata")
def metadata():
    return {
        "model_name": "Random Forest",
        "feature_columns": feature_cols,
        "weather_categories": weather_categories,
        "version": "1.1.0",
    }


@app.post("/predict")
def predict(payload: PredictionRequest):
    try:
        X = build_feature_row(payload.model_dump())
        return prediction_summary(X)
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}") from exc


@app.post("/batch-predict")
def batch_predict(payload: BatchPredictionRequest):
    try:
        predictions = []
        for item in payload.items:
            X = build_feature_row(item.model_dump())
            predictions.append(prediction_summary(X))
        return {"predictions": predictions}
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {exc}") from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.predict_api:app", host="0.0.0.0", port=8000, reload=True)
