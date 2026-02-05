@echo off
:: A batch script which sets up a single virtualenv for the entire full_reporter
:: project, and installs all dependencies.

set VIRTUALENV_DIR=%CD%\venv\Scripts

:: Make new virtualenv
echo "Creating new virtualenv for the project..."
python -m venv venv

echo "Activating virtualenv..."
call %VIRTUALENV_DIR%\activate.bat

echo "Installing dependencies..."
call %VIRTUALENV_DIR%\pip.exe install -r requirements.txt

echo "Finished. Deactivating virtualenv..."
call %VIRTUALENV_DIR%\deactivate.bat

echo.
echo Setup complete! The virtual environment is located at: %CD%\venv
echo To activate it manually, run: venv\Scripts\activate.bat
