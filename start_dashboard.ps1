Set-Location $PSScriptRoot
$ProjectPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$ParentPython = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"

if (Test-Path $ProjectPython) {
    & $ProjectPython -m streamlit run app/dashboard.py
} elseif (Test-Path $ParentPython) {
    & $ParentPython -m streamlit run app/dashboard.py
} else {
    Write-Error "Virtual environment not found. Run: py -3.11 -m venv .venv"
}
