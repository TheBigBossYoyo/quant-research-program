@echo off
setlocal
title Phase 8B Fresh Post-Repair Validation Labeler (15 cases)
cd /d "%~dp0research\phase8b\labeler"
set PYTHONUTF8=1
where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found on PATH. Install Python 3.10+ and tick "Add python.exe to PATH".
  pause
  exit /b 1
)
if not exist "%~dp0research\phase8b\gold2\phase8b_gold2_candidates.csv" (
  echo The fresh validation set has not been drawn yet: research\phase8b\gold2\phase8b_gold2_candidates.csv is missing.
  pause
  exit /b 1
)
echo Starting the 15-case fresh validation labeler. Your browser opens http://127.0.0.1:8767/ - keep this window open.
echo The passage shown is the sentence the rule acted on, with one sentence each side. Nothing is hidden or ranked.
echo Every label is saved to disk immediately; close any time and reopen to resume.
python gold2_labeler.py
if errorlevel 1 pause
endlocal
