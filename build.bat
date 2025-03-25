@echo off
title AlbayanBuild
set VENV_DIR=albayan_env

if not exist %VENV_DIR% (
    echo Creating virtual environment...
    py -3.13 -m venv %VENV_DIR%
)

call %VENV_DIR%\Scripts\activate

echo Updating pip...
python -m pip install --upgrade pip

if exist requirements.txt (
    echo Installing/updating libraries from requirements.txt...
    pip install -r requirements.txt --upgrade
) else (
    echo requirements.txt not found!
    exit /b 1
)

pip show cx-freeze >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing cx-Freeze...
    pip install cx-freeze
)

if exist setup.py (
    echo Building the program with cx-Freeze...
    python setup.py build
) else (
    echo setup.py not found!
    exit /b 1
)

deactivate
echo Done!
pause
