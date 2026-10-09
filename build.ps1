$Host.UI.RawUI.WindowTitle = "AlbayanBuild"
Set-Location -Path $PSScriptRoot

$VENV_DIR = "albayan_env"

if (-not (Test-Path $VENV_DIR)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    py -3.14 -m venv $VENV_DIR
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to create virtual environment!" -ForegroundColor Red
        Pause
        exit 1
    }
}

$activateScript = Join-Path $VENV_DIR "Scripts\Activate.ps1"
if (-not (Test-Path $activateScript)) {
    Write-Host "Activation script not found at $activateScript" -ForegroundColor Red
    Pause
    exit 1
}

Write-Host "Activating virtual environment..." -ForegroundColor Cyan
. $activateScript

Write-Host "Updating pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

if (Test-Path "requirements.txt") {
    Write-Host "Installing/updating libraries from requirements.txt..." -ForegroundColor Cyan
    python -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install dependencies from requirements.txt!" -ForegroundColor Red
        deactivate
        Pause
        exit 1
    }
}
else {
    Write-Host "requirements.txt not found!" -ForegroundColor Red
    deactivate
    Pause
    exit 1
}

if (Test-Path "setup.py") {
    Write-Host "Building the program with cx-Freeze..." -ForegroundColor Cyan
    python setup.py build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Build failed!" -ForegroundColor Red
        deactivate
        Pause
        exit 1
    }
}
else {
    Write-Host "setup.py not found!" -ForegroundColor Red
    deactivate
    Pause
    exit 1
}

deactivate
Write-Host "Build completed successfully!" -ForegroundColor Green
Pause
