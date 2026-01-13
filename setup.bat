@echo off
REM ========================================
REM AI Chatbot - First Time Setup Script
REM ========================================
REM Use this ONLY for initial setup
REM Creates virtual environment and installs dependencies
REM Run once, then use run.bat to start the app

setlocal enabledelayedexpansion

echo.
echo ========================================
echo  🤖 AI Chatbot - First Time Setup
echo ========================================
echo.
echo This script will:
echo  1. Create a virtual environment
echo  2. Install all dependencies
echo  3. Guide you to set up your API key
echo.

REM Check if in correct directory
if not exist "app\streamlit_app.py" (
    echo ERROR: Please run this script from the ai-chatbot-memory folder
    echo Current folder: %cd%
    pause
    exit /b 1
)

REM Check if virtual environment already exists
if exist "genai_env" (
    echo ⚠️  Virtual environment already exists!
    echo If you want to recreate it:
    echo   1. Delete the genai_env folder
    echo   2. Run this script again
    pause
    exit /b 1
)

echo.
echo Step 1: Creating Virtual Environment
echo =====================================
python -m venv genai_env
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo ✓ Virtual environment created

echo.
echo Step 2: Activating Virtual Environment
echo =======================================
call genai_env\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo ✓ Virtual environment activated

echo.
echo Step 3: Installing Dependencies
echo ===============================
echo Installing packages from requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ All packages installed successfully

echo.
echo Step 4: Setting Up API Key
echo ==========================
echo Visit: https://aistudio.google.com/app/apikey
echo Get your free Google Gemini API key
echo.
set /p API_KEY="Paste your API key here (or press Enter to skip for now): "

if not "!API_KEY!"=="" (
    echo.
    echo Creating .env file...
    (
        echo GEMINI_API_KEY=!API_KEY!
    ) > .env
    echo ✓ .env file created with your API key
) else (
    echo.
    echo ℹ️  You can set up the API key later:
    echo   1. Create a .env file in the project root
    echo   2. Add: GEMINI_API_KEY=your_key_here
)

echo.
echo ========================================
echo  ✓ Setup Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Run: run.bat
echo   2. The app will open at http://localhost:8501
echo.
pause
