@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "PYTHONIOENCODING=utf-8"

title Тени пустошей

py -3 main.py

echo.
pause

