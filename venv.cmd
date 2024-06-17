@echo off
title Virtual environment
setlocal enabledelayedexpansion

cd /d "%~dp0"

set /p create_activate=Do you want to Create or Activate the environment? (C/A):

if /i !create_activate! equ C (
    start /wait python -m venv env
          start cmd.exe /k "call env\Scripts\activate.bat && cd /d ""%~dp0"" && pip install -r requirements.txt"
) else if /i !create_activate! equ A (
    start cmd.exe /k "call env\Scripts\activate.bat"
)

exit