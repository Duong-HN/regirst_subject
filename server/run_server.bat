@echo off
title COURSE SERVER
echo Starting Server on 0.0.0.0:8888...
REM %~dp0 refers to the directory where this .bat file is located
python "%~dp0server.py"
pause
