@echo off
echo Testing database connection...
call .\venv\Scripts\activate.bat
echo Virtual environment activated
python test_db_connection.py
pause
