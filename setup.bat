@echo off
echo 🚀 Setting up AI Inventory Management System...

REM Create project directory
mkdir ml1
cd ml1

REM Create virtual environment
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements
pip install -r requirements.txt

REM Create necessary folders
mkdir templates
mkdir models

echo 📁 Please copy the following files into the inventory_ai directory:
echo    - app.py
echo    - templates/index.html
echo    - test_data.py
echo    - requirements.txt

echo.
echo To run the application:
echo 1. python app.py
echo 2. Open http://localhost:5000
echo.
echo To test with sample data:
echo python test_data.py

pause