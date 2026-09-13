@echo off
cd /d "%~dp0"
set PYTHONPATH=src
python -m pete_discovery.server --port 8792 --state runtime
