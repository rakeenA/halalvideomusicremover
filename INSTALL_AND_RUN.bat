@echo off
cls
echo.
echo ========================================
echo Video Downloader & Music Remover
echo ========================================
echo.
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo.
    echo Please install Python from: https://www.python.org/downloads/ or from Windows Store (less optimal)!
    echo Make sure to check "Add Python to PATH" or add it manually if you've downloaded it from Windows Store! 
    echo.
    pause
    exit /b 1
)
echo ✓ Python found
echo.
echo Installing/updating dependencies...
pip install -r requirements.txt --quiet
echo ✓ Dependencies ready
echo.
echo Starting application...
echo.
python -m src.main
pause
