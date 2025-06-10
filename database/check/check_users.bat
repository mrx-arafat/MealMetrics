@echo off
echo ========================================
echo MealMetrics Database User Checker
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if we're in the database/check directory
if not exist "quick_db_check.py" (
    echo Error: This doesn't look like the database/check directory
    echo Please run this from the MealMetrics/database/check folder
    pause
    exit /b 1
)

echo Checking database...
echo.

REM Run the quick check script
python quick_db_check.py

echo.
echo ========================================
echo Check complete! Press any key to exit.
pause >nul
