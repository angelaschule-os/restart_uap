@echo off

REM Get the Git version hash
for /f %%i in ('git rev-parse --short HEAD') do set git_hash=%%i

REM Write the Git version hash to git_version.py
echo GIT_HASH = '%git_hash%' > git_version.py

REM Build the binary with PyInstaller
python -m PyInstaller --onefile --name restart_uap main.py
