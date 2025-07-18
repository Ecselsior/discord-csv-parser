:: Authored by AI: Google's Gemini Model
@echo off
echo =========================================
echo  Setting up Python Virtual Environment
echo =========================================
python -m venv .venv
if %errorlevel% neq 0 (
    echo Failed to create virtual environment. Please ensure Python 3.13 is installed and in your PATH.
    pause
    exit /b %errorlevel%
)

echo =========================================
echo  Activating Virtual Environment
echo =========================================
call .\.venv\Scripts\activate

echo =========================================
echo  Installing Dependencies
echo =========================================
pip install pandas matplotlib requests beautifulsoup4
if %errorlevel% neq 0 (
    echo Failed to install dependencies.
    pause
    exit /b %errorlevel%
)

echo.
echo Setup complete. You can now run the application using launch.bat
pause