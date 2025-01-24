@echo off
call .\env\Scripts\activate.bat
pip install ffmpeg
pip install -r requirements.txt
streamlit run app.py
