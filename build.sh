#!/bin/bash

pip install -r requirements.txt pyinstaller staticx

# Get the Git version hash
git_hash=$(git rev-parse --short HEAD)

# Write the Git version hash to git_version.py
echo "GIT_HASH = '${git_hash}'" > git_version.py

# Build the binary with PyInstaller
python -m PyInstaller --onefile --name restart_uap main.py

# Bundle dynamic executables with their library dependencies so they can be run
# anywhere, just like a static executable.

if [ -z "$GITHUB_ACTION" ]
then
  echo "GITHUB_ACTION is not present. staticx can be run."
  staticx dist/restart_uap dist/restart_uap
else
  echo "GITHUB_ACTION is present. staticx cannot be run in a GitHub Action environment."
fi
