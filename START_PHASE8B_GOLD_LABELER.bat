@echo off
setlocal
title Phase 8B Gold Validation Labeler (60 cases)
cd /d "%~dp0research\phase8b\labeler"
set PYTHONUTF8=1
where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found on PATH. Install Python 3.10+ and tick "Add python.exe to PATH".
  pause
  exit /b 1
)
if not exist "%~dp0research\phase8b\gold\phase8b_gold_candidates.csv" (
  echo The gold set has not been drawn yet: research\phase8b\gold\phase8b_gold_candidates.csv is missing.
  pause
  exit /b 1
)
echo Starting the 60-case gold labeler. Your browser opens http://127.0.0.1:8766/ - keep this window open.
echo Every label is saved to disk immediately; close any time and reopen to resume.
python gold_labeler.py
if errorlevel 1 pause
endlocal
