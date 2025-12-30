@echo off
REM SOTA Agent Framework - One-Time Setup Script (Windows)

echo.
echo Setting up SOTA Agent Framework...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.9+ first.
    exit /b 1
)

echo Installing dependencies...
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo Failed to install dependencies. Please check the error above.
    exit /b 1
)

echo.
echo Installing framework as editable package...
python -m pip install -e .

if errorlevel 1 (
    echo Failed to install framework. Please check the error above.
    exit /b 1
)

echo.
echo Setup complete!
echo.
echo You're ready to generate agent projects!
echo.
echo Try it now:
echo   python template_generator.py --domain "your_domain" --output ./your_project
echo.
echo See GETTING_STARTED.md for more information.
echo.
pause

