$Host.UI.RawUI.WindowTitle = "Virtual environment"
Set-Location -Path $PSScriptRoot

$choice = Read-Host "Do you want to Create or Activate the environment? (C/A)"

if ($choice -ieq "C") {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    Start-Process -Wait "py" -ArgumentList "-3.14", "-m", "venv", "albayan_env"

    $activateScript = Join-Path $PSScriptRoot "albayan_env\Scripts\Activate.ps1"
    if (Test-Path $activateScript) {
        Write-Host "Activating environment, updating pip, and installing requirements..." -ForegroundColor Cyan
        Start-Process "powershell.exe" -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", "Set-Location '$PSScriptRoot'; & '$activateScript'; python -m pip install --upgrade pip; python -m pip install -r requirements.txt"
    } else {
        Write-Host "Virtual environment creation may have failed. Could not find $activateScript" -ForegroundColor Red
        Pause
    }
}
elseif ($choice -ieq "A") {
    $activateScript = Join-Path $PSScriptRoot "albayan_env\Scripts\Activate.ps1"
    if (Test-Path $activateScript) {
        Write-Host "Activating existing environment..." -ForegroundColor Cyan
        Start-Process "powershell.exe" -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", "Set-Location '$PSScriptRoot'; & '$activateScript'"
    } else {
        Write-Host "Virtual environment not found! Please run again and choose C to create it first." -ForegroundColor Red
        Pause
    }
}
else {
    Write-Host 'Invalid choice. Please enter C or A.' -ForegroundColor Red
    Pause
}

exit
