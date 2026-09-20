@echo off
setlocal
title Phase 8B Human Labeler
cd /d "%~dp0"
set PYTHONUTF8=1
where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found on PATH. Install Python 3.10+ from python.org and tick "Add python.exe to PATH".
  pause
  exit /b 1
)
echo Starting the Phase 8B labeler (standard library only, nothing to install)...
echo Your browser will open at http://127.0.0.1:8765/  -  keep this window open while labeling.
echo Labels are saved to disk after every click; close this window whenever you like and reopen later to resume.
python "%~dp0labeler\labeler_app.py"
if errorlevel 1 pause
endlocal
