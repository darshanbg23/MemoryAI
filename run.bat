@echo off
REM ========================================
REM AI Chatbot - Run Script
REM ========================================
REM Use this to start the app after setup
REM Activates virtual environment and runs Streamlit

echo.
echo ========================================
echo  🤖 AI Chatbot - Starting App
echo ========================================
echo.

REM Check if in correct directory
if not exist "app\streamlit_app.py" (
    echo ERROR: Please run this script from the ai-chatbot-memory folder
    echo Current folder: %cd%
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "genai_env" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

echo Activating virtual environment...
call genai_env\Scripts\activate.bat

if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo ✓ Virtual environment activated
echo.
echo Starting Streamlit app...
echo Opening at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

python -m streamlit run app/streamlit_app.py

pause
