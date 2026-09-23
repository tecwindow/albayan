$Host.UI.RawUI.WindowTitle = "Virtual environment"

Set-Location -Path $PSScriptRoot

$choice = Read-Host "Do you want to Create or Activate the environment? (C/A)"

if ($choice -ieq "C") {
    Write-Host "Creating virtual environment..."
    Start-Process -Wait "py" -ArgumentList "-3.14", "-m", "venv", "albayan_env"

    Write-Host "Activating environment, updating pip, and installing requirements..."
    Start-Process "powershell.exe" -ArgumentList "-NoExit", "-Command",
    "Set-Location '$PSScriptRoot'; & 'albayan_env\Scripts\Activate.ps1'; python -m pip install --upgrade pip; pip install -r requirements.txt"
}
elseif ($choice -ieq "A") {
    Write-Host "Activating existing environment..."
    Start-Process "powershell.exe" -ArgumentList "-NoExit", "-Command",
    "Set-Location '$PSScriptRoot'; & 'albayan_env\Scripts\Activate.ps1'"
}
else {
    Write-Host 'Invalid choice. Please enter C or A.' -ForegroundColor Red
}

exit
