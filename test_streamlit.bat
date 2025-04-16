@echo off
echo Testing Streamlit...
call .\venv\Scripts\activate.bat
echo Virtual environment activated
streamlit run test_streamlit.py
pause
