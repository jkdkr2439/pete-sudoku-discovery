@echo off
cd /d "%~dp0"
set PYTHONPATH=src
set PYTHONDONTWRITEBYTECODE=1
python -m pete_discovery.server --port 8792 --state runtime
