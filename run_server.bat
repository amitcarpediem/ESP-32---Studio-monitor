@echo off
title ESP32 Studio Silence & Environment Monitor Server
cd /d "%~dp0"
echo ========================================================
echo  Starting ESP32 Studio Noise & Environment Monitor...
echo ========================================================
echo.
echo Opening browser at http://localhost:5000 ...
start "" http://localhost:5000
python server.py
pause
