@echo off
title ESP32 Telemetry Simulator
cd /d "%~dp0"
echo ========================================================
echo  Starting ESP32 Sensor Simulator...
echo ========================================================
echo.
python simulate_esp32.py
pause
