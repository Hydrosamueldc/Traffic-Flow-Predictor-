# Beginner run guide

This guide is for running the project on Windows.

## 1. Open the correct folder

The real project is the inner folder:

```powershell
cd C:\Users\PC\Downloads\traffic-flow-ml\traffic-flow-ml
```

## 2. Install the requirements

Run this once:

```powershell
..\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 3. Start everything with one command

From the project folder, run:

```powershell
.\start_project.ps1
```

This opens two PowerShell windows:

- one for the FastAPI backend
- one for the Streamlit dashboard

## 4. Manual option

If you prefer to run them yourself, open two terminals.

Terminal 1:

```powershell
cd C:\Users\PC\Downloads\traffic-flow-ml\traffic-flow-ml
.\start_api.ps1
```

Terminal 2:

```powershell
cd C:\Users\PC\Downloads\traffic-flow-ml\traffic-flow-ml
.\start_dashboard.ps1
```

## 5. Browser links

API:

```text
http://127.0.0.1:8000/health
```

Dashboard:

```text
http://localhost:8501
```

If port `8501` is busy, Streamlit may choose another port and print the link in the terminal.

## 6. Optional `.env`

Copy `.env.example` to `.env` if you want to change the API URL:

```powershell
Copy-Item .env.example .env
```

Default:

```text
TRAFFIC_API_URL=http://127.0.0.1:8000
```
