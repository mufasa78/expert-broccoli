@echo off
echo Starting Streamlit Application...
call .\venv\Scripts\activate.bat
echo Virtual environment activated
echo Running Streamlit app on port 8501...
streamlit run streamlit_app.py
pause
