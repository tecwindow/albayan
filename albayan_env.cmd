@echo off
title Virtual environment
setlocal enabledelayedexpansion

cd /d "%~dp0"

set /p create_activate=Do you want to Create or Activate the environment? (C/A):

if /i !create_activate! equ C (
    start /wait py -3.12 -m venv albayan_env
          start cmd.exe /k "call albayan_env\Scripts\activate.bat && cd /d ""%~dp0"" && pip install -r requirements.txt"
) else if /i !create_activate! equ A (
    start cmd.exe /k "call albayan_env\Scripts\activate.bat"
)

exit