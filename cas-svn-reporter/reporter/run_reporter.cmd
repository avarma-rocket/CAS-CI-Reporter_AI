@echo off
:: A script for running the Jenkins Reporter program in a the 
:: virtual environment. Arguments passed to this script are
:: passed to the python program.

set VIRTUALENV_DIR=%CD%\venv\Scripts
set SRC_DIR=%CD%\src

echo "Activating virtualenv..."
call %VIRTUALENV_DIR%\activate.bat


set arg_string=
:parse_string
if not "%~1"=="" (
    if not defined arg_string (
        set "arg_string=%~1 "
    ) else (
        set "arg_string=%arg_string%%~1 "
    )
    shift
    goto :parse_string
)

set PYTHONHTTPSVERIFY=0
echo "Running python script..."
call %VIRTUALENV_DIR%\python.exe %SRC_DIR%\jenkins_reporter.py %arg_string%
set arg_string=

echo "Finished. Deactivating virtualenv..."
call %VIRTUALENV_DIR%\deactivate.bat
