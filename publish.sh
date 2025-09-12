#!/bin/bash
# Synapse Language Publishing Script for Unix/Linux/macOS
# Usage: ./publish.sh [all|pypi|vscode|npm|github] [--dry-run] [--test-pypi]

set -e  # Exit on error

echo "================================================================================"
echo "Synapse Language Publisher"
echo "================================================================================"

# Check Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    exit 1
fi

# Check pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "[ERROR] pip3 is not installed"
    exit 1
fi

# Install required packages if missing
echo "Checking dependencies..."

if ! pip3 show build &> /dev/null; then
    echo "Installing build..."
    pip3 install build
fi

if ! pip3 show twine &> /dev/null; then
    echo "Installing twine..."
    pip3 install twine
fi

# Check for VS Code extension tools if publishing to VS Code
if [[ " $* " == *" vscode "* ]] || [[ " $* " == *" all "* ]]; then
    if ! command -v npm &> /dev/null; then
        echo "[WARNING] npm is not installed. VS Code extension publishing will be skipped."
    elif ! command -v vsce &> /dev/null; then
        echo "Installing vsce..."
        npm install -g vsce
    fi
fi

# Check for GitHub CLI if creating releases
if [[ " $* " == *" github "* ]] || [[ " $* " == *" all "* ]]; then
    if ! command -v gh &> /dev/null; then
        echo "[WARNING] GitHub CLI is not installed. GitHub release creation will be skipped."
        echo "Install from: https://cli.github.com/"
    fi
fi

# Run the publisher
python3 publish_all.py "$@"

if [ $? -eq 0 ]; then
    echo ""
    echo "[SUCCESS] Publishing completed successfully!"
else
    echo ""
    echo "[ERROR] Publishing failed. Check the output above for details."
    exit 1
fi