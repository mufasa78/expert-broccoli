@echo off
echo Starting Flask Application...
call .\venv\Scripts\activate.bat
echo Virtual environment activated
echo Running Flask app on port 5000...
python main.py
pause
