@echo off
:: A batch script which sets up a new virtualenv for the project, and installs
:: all dependencies for the project.

set VIRTUALENV_DIR=%CD%\venv\Scripts
set SRC_DIR=%CD%\src

:: Make new virtualenv
echo "Creating new virtualenv for the project..."
py -m venv venv

echo "Activating virtualenv..."
call %VIRTUALENV_DIR%\activate.bat

echo "Installing dependencies..."
call %VIRTUALENV_DIR%\pip.exe install -r requirements.txt

echo "Finished. Deactivating virtualenv..."
call %VIRTUALENV_DIR%\deactivate.bat