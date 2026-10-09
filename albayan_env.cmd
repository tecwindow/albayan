@echo off
chcp 65001 >nul
title Virtual environment
setlocal enabledelayedexpansion

cd /d "%~dp0"

set /p create_activate=Do you want to Create or Activate the environment? (C/A): 

if /i "!create_activate!" equ "C" (
    echo Creating virtual environment...
    py -3.14 -m venv albayan_env
    if errorlevel 1 (
        echo Failed to create virtual environment!
        pause
        exit /b 1
    )
    start cmd.exe /k "cd /d ""%~dp0"" && call albayan_env\Scripts\activate.bat && python -m pip install --upgrade pip && python -m pip install -r requirements.txt"
) else if /i "!create_activate!" equ "A" (
    if not exist "albayan_env\Scripts\activate.bat" (
        echo Virtual environment not found! Please choose C to create it first.
        pause
        exit /b 1
    )
    start cmd.exe /k "cd /d ""%~dp0"" && call albayan_env\Scripts\activate.bat"
) else (
    echo Invalid choice. Please enter C or A.
    pause
    exit /b 1
)

exit /b 0
