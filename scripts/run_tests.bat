@echo off
REM Windows batch script to run all tests

echo Running tests for microservices application...
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

REM Run the Python test script
python "%SCRIPT_DIR%run_tests.py" --project-root "%PROJECT_ROOT%" %*
