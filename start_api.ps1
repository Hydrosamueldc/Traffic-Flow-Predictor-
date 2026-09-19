Set-Location $PSScriptRoot
$ProjectPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$ParentPython = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"

if (Test-Path $ProjectPython) {
    & $ProjectPython -m uvicorn app.predict_api:app --host 127.0.0.1 --port 8000 --reload
} elseif (Test-Path $ParentPython) {
    & $ParentPython -m uvicorn app.predict_api:app --host 127.0.0.1 --port 8000 --reload
} else {
    Write-Error "Virtual environment not found. Run: py -3.11 -m venv .venv"
}
