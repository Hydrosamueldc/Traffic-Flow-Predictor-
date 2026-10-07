# Traffic Flow Predictor

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python application](https://github.com/Hydrosamueldc/Traffic-Flow-Predictor-/actions/workflows/python-app.yml/badge.svg)](https://github.com/Hydrosamueldc/Traffic-Flow-Predictor-/actions/workflows/python-app.yml)

Predict hourly traffic volume on the I-94 westbound highway corridor from time, weather, holidays, and recent traffic observations. The Streamlit dashboard lets you explore different conditions, view the model's estimate in vehicles per hour, and see an animated preview of traffic intensity.

The predictions come from a Random Forest model served through FastAPI. The dashboard also shows a range based on variation between the model's trees; this range is approximate, rather than a calibrated confidence interval.

**Live dashboard:** [Open Traffic Flow Predictor](https://samuel-traffic-flow-predictor.streamlit.app/)

**Hosted prediction API:** [traffic-flow-predictor-njqc.onrender.com](https://traffic-flow-predictor-njqc.onrender.com)

[API documentation](https://traffic-flow-predictor-njqc.onrender.com/docs) | [Health check](https://traffic-flow-predictor-njqc.onrender.com/health)

The API runs on Render's free tier. After inactivity, the first request may take about a minute while the service wakes.

## Background

I built this project as a companion to my undergraduate thesis on the Lighthill-Whitham-Richards (LWR) traffic-flow model. The thesis used Upwind and Lax-Wendroff schemes to simulate how traffic density changes along a road. Here, I use historical observations to predict hourly traffic volume.

## Dataset

Source: [Metro Interstate Traffic Volume](https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume), UCI Machine Learning Repository.

The raw data contains hourly I-94 westbound traffic volume and weather observations from October 2012 to September 2018.

Main target:

```text
traffic_volume = number of vehicles passing the sensor in one hour
```

## Model inputs

Inputs include:

- hour of day
- day of week
- month
- weekend flag
- holiday flag
- temperature
- rain
- snow
- cloud cover
- weather category
- traffic volume 1 hour ago
- traffic volume 3 hours ago
- traffic volume 24 hours ago
- rolling 3-hour traffic average

Supply recent traffic observations when available; these inputs help the model capture the daily traffic cycle.

## Data preparation

The project cleans the original dataset by:

- removing duplicate timestamp rows
- removing impossible temperature readings of 0 Kelvin
- converting the sparse holiday column into a binary holiday flag
- converting temperature from Kelvin to Celsius
- encoding hour and day of week cyclically
- one-hot encoding weather categories
- adding lag and rolling traffic features

Final cleaned dataset size: 40,565 hourly records.

## Model performance

Models are evaluated on a chronological split, with the test period following the training period. MAE and RMSE are measured in vehicles per hour.

| Model | MAE | RMSE | R2 |
|---|---:|---:|---:|
| Linear Regression | 370.2 | 495.6 | 0.937 |
| Random Forest | 149.9 | 243.5 | 0.985 |
| Gradient Boosting | 196.8 | 299.2 | 0.977 |

Random Forest achieved the lowest test error and is used by the API. These results are recorded in [models/metrics.json](models/metrics.json).

## Results and visualizations

### Traffic patterns in the dataset

Traffic is lowest overnight, rises sharply during the morning commute, and reaches its highest average level during the afternoon rush period. Weekday traffic is also noticeably higher than weekend traffic.

![Traffic patterns by hour, weekday, weather, and volume distribution](figures/eda_overview.png)

### Model evaluation

The predicted-versus-actual plot shows how closely predictions follow measured traffic. The one-week comparison shows the model following the repeated daily traffic cycle, while the residual chart shows the remaining prediction errors.

![Random Forest prediction evaluation](figures/model_evaluation.png)

### Input variables compared with traffic volume

These plots show how time, weather, cloud cover, and holidays relate to the number of vehicles recorded per hour. They help explain which patterns are available to the model before training.

![Predictor variables compared with traffic volume](figures/variable_vs_target.png)

To regenerate the figures, run:

```bash
python scripts/02_eda.py
python scripts/04_evaluate_and_plot.py
python scripts/05_variable_vs_target_plots.py
```

## Stack

| Tool | Purpose |
|---|---|
| Python | Main programming language |
| pandas | Data cleaning and feature preparation |
| NumPy | Numerical calculations |
| scikit-learn | Machine-learning models |
| Matplotlib | Charts and plots |
| Joblib | Saves and loads the trained model |
| FastAPI | Prediction API backend |
| Uvicorn | Runs the FastAPI server |
| Streamlit | Interactive dashboard |
| Requests | Lets the dashboard call the API |
| Pytest | Automated tests |
| Docker | Packages and runs the FastAPI backend consistently |

## Repository structure

```text
traffic-flow-ml/
  app/
    dashboard.py          Streamlit dashboard
    predict_api.py        FastAPI prediction service
  data/
    metro_traffic_raw.csv Raw data
    traffic_clean.csv     Cleaned data
  figures/
    eda_overview.png
    model_evaluation.png
    variable_vs_target.png
  models/
    best_model.pkl
    feature_columns.pkl
    metrics.json
    feature_importances.csv
  scripts/
    01_clean_and_feature_engineer.py
    02_eda.py
    03_train_models.py
    04_evaluate_and_plot.py
    05_variable_vs_target_plots.py
  tests/
    test_api.py
  Dockerfile
  requirements.txt
  pytest.ini
  README.md
```

## How to run locally on Windows

Clone the repository and enter the project folder:

```powershell
git clone https://github.com/Hydrosamueldc/Traffic-Flow-Predictor-.git
cd Traffic-Flow-Predictor-
```

Create a Python 3.11 virtual environment and install the dependencies:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Start the API in terminal 1:

```powershell
python -m uvicorn app.predict_api:app --host 127.0.0.1 --port 8000 --reload
```

Leave terminal 1 running. Open another terminal, go to the same folder, and start the dashboard:

```powershell
cd Traffic-Flow-Predictor-
.\.venv\Scripts\Activate.ps1
python -m streamlit run app/dashboard.py
```

Streamlit opens the dashboard in the default browser.

Alternatively, start both services with one command:

```powershell
.\start_project.ps1
```

For a step-by-step walkthrough, see [run.md](run.md).

## Configuration

The dashboard reads the API URL from the `TRAFFIC_API_URL` environment variable.

For local use, copy the example file:

```powershell
Copy-Item .env.example .env
```

Default value:

```text
TRAFFIC_API_URL=http://127.0.0.1:8000
```

## API examples

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Single prediction:

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "hour": 17,
    "day_of_week": 2,
    "month": 10,
    "temp_c": 15.0,
    "rain_1h": 0.1,
    "snow_1h": 0.0,
    "clouds_all": 40,
    "is_holiday": 0,
    "weather_main": "Clouds",
    "traffic_volume_lag_1h": 3200,
    "traffic_volume_lag_3h": 3100,
    "traffic_volume_lag_24h": 3000,
    "rolling_3h_mean": 3150
  }'
```

Batch prediction:

```bash
curl -X POST http://127.0.0.1:8000/batch-predict \
  -H "Content-Type: application/json" \
  -d '{"items":[{"hour":17,"day_of_week":2,"weather_main":"Clouds"},{"hour":3,"day_of_week":6,"weather_main":"Snow"}]}'
```

Model metadata:

```bash
curl http://127.0.0.1:8000/metadata
```

## Docker

The API can also run in Docker. Render uses the same [Dockerfile](Dockerfile), configured through [render.yaml](render.yaml).

Build the image:

```bash
docker build -t traffic-flow-ml .
```

Run the API container:

```bash
docker run -p 8000:8000 traffic-flow-ml
```

The container starts Uvicorn, exposes the FastAPI service, and uses the port supplied by the hosting platform.

## Tests

Run:

```powershell
python -m pytest -q
```

The tests check that:

- feature rows include the expected lag features
- the prediction endpoint returns a valid prediction
- the prediction endpoint returns an interval estimate
- the metadata endpoint works
- batch prediction returns multiple predictions

## Limitations

- The model is trained on one highway corridor, so it should not be treated as a universal traffic predictor.
- The dataset ends in 2018, so production use would require retraining with current data.
- The prediction interval is an approximate range from Random Forest tree variation, not a statistically calibrated guarantee.
- The dashboard animation is a visual traffic-intensity preview, not a physical traffic simulation.
- The public API does not include authentication, rate limiting, or production monitoring.
- The free Render service may take about a minute to wake after inactivity.

## Potential extensions

- Calibrate the prediction interval against real forecasting errors.
- Add authentication and rate limiting for public deployment.
- Add monitoring and scheduled retraining.
- Validate the model on another road corridor.
- Add an LWR numerical simulation module from the undergraduate thesis.
- Build a hybrid workflow where ML predicts demand and the LWR model simulates congestion propagation.

## Deployment

The project uses two hosted services:

| Component | Platform | Purpose |
|---|---|---|
| [Dashboard](https://samuel-traffic-flow-predictor.streamlit.app/) | Streamlit Community Cloud | Displays the interactive prediction interface |
| Prediction API | Render | Loads the trained model and returns predictions |

Backend health check: [traffic-flow-predictor-njqc.onrender.com/health](https://traffic-flow-predictor-njqc.onrender.com/health)

The dashboard stores the backend address in its Streamlit Cloud secrets:

```toml
TRAFFIC_API_URL = "https://traffic-flow-predictor-njqc.onrender.com"
```

The free Render service sleeps after inactivity. The first prediction may therefore take up to a minute while the service wakes; later predictions should be faster.

## Author

Adegboyega Samuel

## License

[MIT](LICENSE)
