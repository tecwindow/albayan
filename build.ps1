$VENV_DIR = "albayan_env"

if (-not (Test-Path $VENV_DIR)) {
    Write-Host "Creating virtual environment..."
    py -3.14 -m venv $VENV_DIR
}


$activateScript = Join-Path $VENV_DIR "Scripts\Activate.ps1"
Write-Host "Activating virtual environment..."
. $activateScript


Write-Host "Updating pip..."
python -m pip install --upgrade pip


if (Test-Path "requirements.txt") {
    Write-Host "Installing/updating libraries from requirements.txt..."
    pip install -r requirements.txt --upgrade
}
else {
    Write-Host "requirements.txt not found!" -ForegroundColor Red
    exit 1
}



if (Test-Path "setup.py") {
    Write-Host "Building the program with cx-Freeze..."
    python setup.py build
}
else {
    Write-Host "setup.py not found!" -ForegroundColor Red
    exit 1
}


deactivate

Write-Host "Done!" -ForegroundColor Green
Pause
