import pytest
from fastapi.testclient import TestClient

from app.predict_api import app, build_feature_row


@pytest.fixture
def sample_payload():
    return {
        "hour": 17,
        "day_of_week": 2,
        "month": 10,
        "temp_c": 15.0,
        "rain_1h": 0.1,
        "snow_1h": 0.0,
        "clouds_all": 40,
        "is_holiday": 0,
        "weather_main": "Clouds",
        "traffic_volume_lag_1h": 3200.0,
        "traffic_volume_lag_3h": 3100.0,
        "traffic_volume_lag_24h": 3000.0,
        "rolling_3h_mean": 3150.0,
    }


def test_build_feature_row_includes_lag_features(sample_payload):
    row = build_feature_row(sample_payload)

    required_cols = {
        "traffic_volume_lag_1h",
        "traffic_volume_lag_3h",
        "traffic_volume_lag_24h",
        "rolling_3h_mean",
    }

    assert required_cols.issubset(row.columns)
    assert row.loc[0, "traffic_volume_lag_1h"] == 3200.0
    assert row.loc[0, "rolling_3h_mean"] == 3150.0


def test_predict_endpoint_returns_prediction(sample_payload):
    client = TestClient(app)
    response = client.post("/predict", json=sample_payload)

    assert response.status_code == 200
    data = response.json()
    assert "predicted_traffic_volume" in data
    assert "prediction_interval" in data
    assert data["predicted_traffic_volume"] > 0
    assert data["prediction_interval"]["lower"] >= 0
    assert data["prediction_interval"]["upper"] >= data["prediction_interval"]["lower"]


def test_metadata_endpoint_returns_model_info():
    client = TestClient(app)
    response = client.get("/metadata")

    assert response.status_code == 200
    data = response.json()
    assert "model_name" in data
    assert "feature_columns" in data
    assert len(data["feature_columns"]) > 0


def test_batch_predict_endpoint_returns_multiple_predictions(sample_payload):
    client = TestClient(app)
    response = client.post(
        "/batch-predict",
        json={"items": [sample_payload, sample_payload]},
    )

    assert response.status_code == 200
    data = response.json()
    assert "predictions" in data
    assert len(data["predictions"]) == 2
    assert all(item["predicted_traffic_volume"] > 0 for item in data["predictions"])
    assert all("prediction_interval" in item for item in data["predictions"])
