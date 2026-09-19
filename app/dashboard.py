import os
from pathlib import Path

import requests
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]


def load_env_file() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env_file()


def get_api_url() -> str:
    """Read the backend URL locally or from Streamlit Community Cloud secrets."""
    configured_url = os.getenv("TRAFFIC_API_URL")
    if not configured_url:
        try:
            configured_url = st.secrets.get("TRAFFIC_API_URL")
        except (FileNotFoundError, KeyError):
            configured_url = None

    return (configured_url or "http://127.0.0.1:8000").rstrip("/")


API_URL = get_api_url()
IS_LOCAL_API = API_URL.startswith(("http://127.0.0.1", "http://localhost"))
WEATHER_OPTIONS = ["Clear", "Clouds", "Rain", "Snow", "Fog", "Mist", "Haze"]


st.set_page_config(
    page_title="Traffic flow predictor",
    page_icon=":material/traffic:",
    layout="wide",
)


def traffic_level(volume: float) -> tuple[str, str, int]:
    if volume < 1800:
        return "Light", "#22c55e", 3
    if volume < 3500:
        return "Moderate", "#f59e0b", 5
    return "Heavy", "#ef4444", 7


def apply_display_mode(dark_mode: bool) -> None:
    if not dark_mode:
        return

    st.html(
        """
        <style>
        .stApp {
            background: #0f172a;
            color: #e5e7eb;
        }
        [data-testid="stSidebar"] {
            background: #111827;
        }
        [data-testid="stHeader"] {
            background: rgba(15, 23, 42, 0.88);
        }
        [data-testid="stBaseButton-secondary"],
        [data-testid="stBaseButton-primary"] {
            border-color: #334155;
        }
        </style>
        """
    )


def render_road_scene(volume: float | None, dark_mode: bool) -> None:
    display_volume = 3150.0 if volume is None else volume
    level, accent, car_count = traffic_level(display_volume)
    speed = max(4.5, 11 - min(display_volume, 5200) / 650)
    scene_background = (
        "linear-gradient(#111827 0 28%, #1f2937 28% 80%, #0f172a 80%)"
        if dark_mode
        else "linear-gradient(#d9f2e3 0 28%, #4b5563 28% 80%, #d9f2e3 80%)"
    )
    border_color = "#334155" if dark_mode else "#d6dee8"
    badge_background = "rgba(15,23,42,.92)" if dark_mode else "rgba(255,255,255,.92)"
    badge_text = "#e5e7eb" if dark_mode else "#0f172a"
    shoulder = "#64748b" if dark_mode else "#cbd5e1"

    cars = []
    colors = ["#2563eb", "#f97316", "#16a34a", "#dc2626", "#7c3aed", "#0891b2", "#facc15"]
    for index in range(car_count):
        lane_top = 37 if index % 2 == 0 else 94
        delay = -(index * 1.35)
        width = 46 if index % 3 else 54
        cars.append(
            f"""
            <div class="car" style="
                --lane-top:{lane_top}px;
                --delay:{delay}s;
                --speed:{speed + (index % 3) * 0.7}s;
                --car-color:{colors[index % len(colors)]};
                --car-width:{width}px;
            "><span></span></div>
            """
        )

    st.html(
        f"""
        <style>
        .traffic-scene {{
            border: 1px solid {border_color};
            border-radius: 8px;
            overflow: hidden;
            background: {scene_background};
            height: 190px;
            position: relative;
            box-shadow: inset 0 0 0 1px rgba(255,255,255,0.35);
        }}
        .traffic-scene .skyline {{
            position: absolute;
            top: 14px;
            left: 0;
            right: 0;
            height: 28px;
            background:
                linear-gradient(90deg, transparent 0 8%, #94a3b8 8% 11%, transparent 11% 18%, #64748b 18% 22%, transparent 22% 32%, #94a3b8 32% 36%, transparent 36% 100%);
            opacity: .45;
        }}
        .traffic-scene .road-line {{
            position: absolute;
            top: 88px;
            left: 0;
            right: 0;
            height: 5px;
            background: repeating-linear-gradient(90deg, #f8fafc 0 44px, transparent 44px 82px);
            opacity: .9;
        }}
        .traffic-scene .shoulder {{
            position: absolute;
            left: 0;
            right: 0;
            height: 4px;
            background: {shoulder};
        }}
        .traffic-scene .shoulder.top {{ top: 55px; }}
        .traffic-scene .shoulder.bottom {{ bottom: 38px; }}
        .traffic-badge {{
            position: absolute;
            top: 12px;
            right: 14px;
            background: {badge_background};
            border: 1px solid {border_color};
            border-left: 5px solid {accent};
            color: {badge_text};
            font: 600 14px system-ui, -apple-system, Segoe UI, sans-serif;
            padding: 8px 10px;
            border-radius: 7px;
        }}
        .car {{
            position: absolute;
            top: var(--lane-top);
            left: -80px;
            width: var(--car-width);
            height: 25px;
            background: var(--car-color);
            border-radius: 7px 10px 7px 7px;
            animation: drive var(--speed) linear infinite;
            animation-delay: var(--delay);
            box-shadow: 0 8px 14px rgba(15,23,42,.23);
        }}
        .car::before {{
            content: "";
            position: absolute;
            right: 8px;
            top: 4px;
            width: 14px;
            height: 8px;
            background: rgba(255,255,255,.72);
            border-radius: 3px;
        }}
        .car span::before,
        .car span::after {{
            content: "";
            position: absolute;
            bottom: -5px;
            width: 10px;
            height: 10px;
            border-radius: 999px;
            background: #111827;
            border: 2px solid #e5e7eb;
        }}
        .car span::before {{ left: 7px; }}
        .car span::after {{ right: 7px; }}
        @keyframes drive {{
            from {{ transform: translateX(-90px); }}
            to {{ transform: translateX(calc(100vw + 160px)); }}
        }}
        </style>
        <div class="traffic-scene" role="img" aria-label="Animated road traffic preview">
            <div class="skyline"></div>
            <div class="shoulder top"></div>
            <div class="road-line"></div>
            <div class="shoulder bottom"></div>
            <div class="traffic-badge">{level} traffic preview</div>
            {"".join(cars)}
        </div>
        """
    )


def check_api() -> bool:
    try:
        response = requests.get(f"{API_URL}/health", timeout=3)
        return response.ok
    except requests.RequestException:
        return False


def call_prediction_api(payload: dict) -> dict:
    # Render free services can need close to a minute to wake after inactivity.
    response = requests.post(f"{API_URL}/predict", json=payload, timeout=90)
    response.raise_for_status()
    return response.json()


if "last_prediction" not in st.session_state:
    st.session_state.last_prediction = None


parameter_guide = {
    "Hour of day": "The hour you want to predict for. 17 means 5pm.",
    "Day of week": "The day number. 0 is Monday and 6 is Sunday.",
    "Month": "The month number. This helps the model catch seasonal patterns.",
    "Temperature": "Outside temperature in Celsius.",
    "Rain in the last hour": "How much rain fell in the previous hour, measured in millimetres.",
    "Snow in the last hour": "How much snow fell in the previous hour, measured in millimetres.",
    "Cloud cover": "How cloudy the sky is. 0 means clear, 100 means fully cloudy.",
    "Public holiday": "Whether the day is a public holiday. 0 means no, 1 means yes.",
    "Weather category": "The general weather condition, such as Clear, Rain, Clouds, or Snow.",
    "Traffic volume 1 hour ago": "The number of vehicles counted one hour before the prediction time.",
    "Traffic volume 3 hours ago": "The number of vehicles counted three hours before the prediction time.",
    "Traffic volume 24 hours ago": "The number of vehicles counted at the same hour on the previous day.",
    "Average traffic over last 3 hours": "The average vehicle count across the previous three hours.",
}


with st.sidebar:
    dark_mode = st.toggle("Dark mode", value=False, help="Switches the dashboard and traffic preview to a darker display.")
    st.header("Project status", icon=":material/monitoring:")
    if check_api():
        st.success("FastAPI backend is running", icon=":material/check_circle:")
    else:
        if IS_LOCAL_API:
            st.warning("The prediction service is not connected.", icon=":material/warning:")
            st.caption(
                "Running locally? Start the API. Running online? Add the public backend URL "
                "as TRAFFIC_API_URL in the dashboard settings."
            )
        else:
            st.warning("The prediction service is temporarily unavailable.", icon=":material/warning:")
            st.caption("Check that the backend deployment is running, then try again.")
    st.caption(f"Dashboard backend: {API_URL}")


apply_display_mode(dark_mode)

st.title("Traffic flow predictor", icon=":material/traffic:")
st.caption(
    "Predict hourly traffic volume from time, weather, holidays, and recent traffic history."
)

top_left, top_right = st.columns([1.2, 1], vertical_alignment="center")
with top_left:
    with st.container(border=True):
        st.subheader("What this app does", icon=":material/analytics:")
        st.markdown(
            """
            Enter the time, weather, holiday status, and recent traffic counts. The app compares those details
            with patterns learned from past traffic records and estimates how many vehicles may pass in one hour.

            The road animation changes with the latest result, so the prediction feels easier to read at a glance.
            """
        )
with top_right:
    render_road_scene(st.session_state.last_prediction, dark_mode)


with st.expander("What the inputs mean", icon=":material/help:"):
    st.table(parameter_guide)


with st.form("prediction_form"):
    st.subheader("Prediction inputs", icon=":material/tune:")
    col1, col2, col3 = st.columns(3)

    with col1:
        hour = st.slider("Hour of day", 0, 23, 17, help="0 is midnight, 12 is noon, and 23 is 11pm.")
        day_of_week = st.slider("Day of week", 0, 6, 2, help="0 is Monday and 6 is Sunday.")
        month = st.slider("Month", 1, 12, 10)

    with col2:
        temp_c = st.number_input("Temperature in Celsius", value=15.0)
        rain_1h = st.number_input("Rain in the last hour (mm)", value=0.1, min_value=0.0, step=0.1)
        snow_1h = st.number_input("Snow in the last hour (mm)", value=0.0, min_value=0.0, step=0.1)
        clouds_all = st.slider("Cloud cover (%)", 0, 100, 40)

    with col3:
        is_holiday = st.selectbox("Public holiday", [0, 1], help="0 means no holiday, 1 means holiday.")
        weather_main = st.selectbox("Weather category", WEATHER_OPTIONS)
        traffic_volume_lag_1h = st.number_input(
            "Traffic volume 1 hour ago",
            value=3200.0,
            help="Recent traffic is usually one of the strongest clues for current traffic.",
        )
        traffic_volume_lag_3h = st.number_input("Traffic volume 3 hours ago", value=3100.0)
        traffic_volume_lag_24h = st.number_input("Traffic volume 24 hours ago", value=3000.0)
        rolling_3h_mean = st.number_input(
            "Average traffic over last 3 hours",
            value=3150.0,
            help="This smooths recent traffic history into one helpful feature.",
        )

    submitted = st.form_submit_button("Predict traffic volume", icon=":material/play_arrow:")


if submitted:
    payload = {
        "hour": hour,
        "day_of_week": day_of_week,
        "month": month,
        "temp_c": temp_c,
        "rain_1h": rain_1h,
        "snow_1h": snow_1h,
        "clouds_all": clouds_all,
        "is_holiday": is_holiday,
        "weather_main": weather_main,
        "traffic_volume_lag_1h": traffic_volume_lag_1h,
        "traffic_volume_lag_3h": traffic_volume_lag_3h,
        "traffic_volume_lag_24h": traffic_volume_lag_24h,
        "rolling_3h_mean": rolling_3h_mean,
    }

    try:
        with st.spinner("Contacting the prediction service. The first request may take up to a minute..."):
            result = call_prediction_api(payload)
        prediction = float(result["predicted_traffic_volume"])
        interval = result["prediction_interval"]
        st.session_state.last_prediction = prediction
        level, _, _ = traffic_level(prediction)

        result_col, note_col = st.columns([0.8, 1.2], vertical_alignment="center")
        with result_col:
            st.metric("Predicted traffic volume", f"{prediction:,.1f} vehicles/hour")
            st.caption(
                f"Likely range: {interval['lower']:,.1f} to {interval['upper']:,.1f} vehicles/hour"
            )
            st.badge(level, color="green" if level == "Light" else "orange" if level == "Moderate" else "red")
        with note_col:
            st.markdown(
                """
                The range is estimated from variation across the Random Forest trees. It is useful as a rough
                uncertainty signal, not a formal guarantee. A production system would monitor errors over time.
                """
            )
    except requests.RequestException:
        st.error(
            "The dashboard could not reach the prediction service. Check the backend URL and make sure "
            "the backend deployment is running.",
            icon=":material/error:",
        )
