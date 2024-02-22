@echo off
cls
color 6
echo OUTCREATED VENV 0.0.2
title OUTCREATED SYSTEM 0.0.2

python -m ensurepip --default-pip
python -m venv "%~dp0.venv"
call "%~dp0.venv\Scripts\activate"
call "%~dp0.venv\Scripts\python" "%~dp0app.py"
pause