#!/bin/bash

# Get the Git version hash
git_hash=$(git rev-parse --short HEAD)

# Write the Git version hash to git_version.py
echo "GIT_HASH = '${git_hash}'" > git_version.py

# Build the binary with PyInstaller
pyinstaller --onefile --name restart_uap main.py
