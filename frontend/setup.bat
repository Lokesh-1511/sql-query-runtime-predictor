@echo off
REM SQL Query Runtime Predictor - Frontend Setup Script

echo.
echo ==================================================
echo SQL Query Runtime Predictor - Frontend Setup
echo ==================================================
echo.

REM Check if npm is installed
where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: npm is not installed. Please install Node.js and npm first.
    pause
    exit /b 1
)

echo Found npm!
echo.

echo Installing dependencies...
call npm install

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS: Installation complete!
    echo.
    echo Next steps:
    echo.
    echo 1. Make sure the backend is running on http://localhost:8000
    echo    Run: cd ../ml-sql-query-runtime-prediction-system ^&^& python -m uvicorn api.app:app --reload
    echo.
    echo 2. Start the frontend development server:
    echo    Run: npm run dev
    echo.
    echo 3. Open in browser: http://localhost:5173
    echo.
    pause
) else (
    echo.
    echo ERROR: Installation failed. Please run 'npm install' manually.
    pause
    exit /b 1
)
