@echo off
chcp 65001 >nul
title AlbayanBuild
cd /d "%~dp0"

set VENV_DIR=albayan_env

if not exist "%VENV_DIR%" (
    echo Creating virtual environment...
    py -3.14 -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo Failed to create virtual environment!
        pause
        exit /b 1
    )
)

call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo Failed to activate virtual environment!
    pause
    exit /b 1
)

echo Updating pip...
python -m pip install --upgrade pip

if exist requirements.txt (
    echo Installing/updating libraries from requirements.txt...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Failed to install dependencies!
        call deactivate
        pause
        exit /b 1
    )
) else (
    echo requirements.txt not found!
    call deactivate
    pause
    exit /b 1
)

if exist setup.py (
    echo Building the program with cx-Freeze...
    python setup.py build
    if errorlevel 1 (
        echo Build failed!
        call deactivate
        pause
        exit /b 1
    )
) else (
    echo setup.py not found!
    call deactivate
    pause
    exit /b 1
)

call deactivate
echo Build completed successfully!
pause
