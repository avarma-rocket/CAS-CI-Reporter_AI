@echo off
:: A script for running the Jenkins Reporter program in both
:: cas-component-checkpoint and cas-svn-reporter directories.
:: 
:: Usage: run_reporter.cmd --ccserv-key-file <file> --casci-key-file <file> [other args]

setlocal enabledelayedexpansion

set BASE_DIR=%CD%
set CCSERV_API_KEY_FILE=
set CASCI_API_KEY_FILE=
set OTHER_ARGS=

:: Parse arguments
:parse_args
if "%~1"=="" goto :done_parsing
if /i "%~1"=="--ccserv-key-file" (
    set "CCSERV_API_KEY_FILE=%~2"
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--casci-key-file" (
    set "CASCI_API_KEY_FILE=%~2"
    shift
    shift
    goto :parse_args
)
:: Collect other arguments
if not defined OTHER_ARGS (
    set "OTHER_ARGS=%~1"
) else (
    set "OTHER_ARGS=!OTHER_ARGS! %~1"
)
shift
goto :parse_args

:done_parsing

:: Validate that API key files exist
if not exist "%CCSERV_API_KEY_FILE%" (
    echo ERROR: CCSERV API key file not found: %CCSERV_API_KEY_FILE%
    exit /b 1
)
if not exist "%CASCI_API_KEY_FILE%" (
    echo ERROR: CASCI API key file not found: %CASCI_API_KEY_FILE%
    exit /b 1
)

set PYTHONHTTPSVERIFY=0

:: Set up shared virtualenv path
set VENV_DIR=%BASE_DIR%\venv\Scripts
set CASCI_SRC=%BASE_DIR%\cas-component-checkpoint-main\reporter\src
set CCSERV_SRC=%BASE_DIR%\cas-svn-reporter\reporter\src

echo Activating shared virtualenv...
call %VENV_DIR%\activate.bat

:: Run cas-component-checkpoint reporter (uses CASCI API key)
echo.
echo ============================================================
echo Running cas-component-checkpoint reporter...
echo ============================================================
echo Running python script with CASCI API key...
call %VENV_DIR%\python.exe %CASCI_SRC%\jenkins_reporter.py --api-key-file "%CASCI_API_KEY_FILE%" %OTHER_ARGS%

:: Run cas-svn-reporter (uses CCSERV API key)
echo.
echo ============================================================
echo Running cas-svn-reporter...
echo ============================================================
echo Running python script with CCSERV API key...
call %VENV_DIR%\python.exe %CCSERV_SRC%\jenkins_reporter.py --api-key-file "%CCSERV_API_KEY_FILE%" %OTHER_ARGS%

:: Combine the results files
echo.
echo ============================================================
echo Combining results files...
echo ============================================================
call %VENV_DIR%\python.exe %BASE_DIR%\combine_results.py

:: Upload results to MediaWiki
echo.
echo ============================================================
echo Uploading results to MediaWiki...
echo ============================================================
call %VENV_DIR%\python.exe %BASE_DIR%\upload_wiki.py

:: Clean up generated reports
echo.
echo ============================================================
echo Cleaning up generated reports...
echo ============================================================
if exist "%BASE_DIR%\reports\*.md" (
    del /q "%BASE_DIR%\reports\*.md"
    echo Deleted report files from %BASE_DIR%\reports
) else (
    echo No report files to delete.
)

echo Deactivating virtualenv...
call %VENV_DIR%\deactivate.bat

echo.
echo ============================================================
echo Finished running both reporters, combining results, and uploading to MediaWiki.
echo ============================================================

endlocal
