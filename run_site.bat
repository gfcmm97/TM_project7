@echo off
cd /d %~dp0

call back\.venv\Scripts\activate

start cmd /k "cd back && uvicorn main:app --reload"

set "HTML_PATH=%~dp0front\main.html"
start "" "%HTML_PATH%"