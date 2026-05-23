@echo off
cd D:\SUA LOI GITHUB SHEET PYTHON\deepseek
python weather_notify.py >> weather_log.txt
echo %date% %time% >> weather_log.txt