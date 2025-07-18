:: Authored by AI: Google's Gemini Model
@echo off
echo =========================================
echo  Activating Virtual Environment
echo =========================================
call .\.venv\Scripts\activate
if not exist ".venv\Scripts\activate.bat" (
    echo Virtual environment not found. Please run setup.bat first.
    set /p "dummy=Press ENTER to exit..." >nul
    exit /b 1
)

echo =========================================
echo  Launching Discord Parser Application
echo =========================================
python -u discord_parser\main.py
if %errorlevel% neq 0 (
    echo Application exited with an error.
    set /p "dummy=Press ENTER to exit..." >nul
    exit /b %errorlevel%
)

echo.
echo Application closed.
set /p "dummy=Press ENTER to exit..." >nul