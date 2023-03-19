#!/bin/bash

pip install -r requirements.txt pyinstaller staticx

# Get the Git version hash
git_hash=$(git rev-parse --short HEAD)

# Write the Git version hash to git_version.py
echo "GIT_HASH = '${git_hash}'" > git_version.py

# Build the binary with PyInstaller
pyinstaller --onefile --name restart_uap main.py

# Bundle dynamic executables with their library dependencies so they can be run
# anywhere, just like a static executable.
staticx dist/restart_uap dist/restart_uap
