@echo off
setlocal
cd /d %~dp0
python -m pip install -r app\requirements.txt
call npm install
call npm run dist:win
pause
