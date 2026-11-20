@echo off
call venv\Scripts\activate
start "" http://localhost:8501
streamlit run app.py --server.port 8501 --server.headless true --server.fileWatcherType none --browser.gatherUsageStats false --theme.base dark