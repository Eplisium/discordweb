@echo off
:start_bot1
title web_server
py web_server.py
timeout /t 5
goto start_bot1
