#!/bin/bash

clear
echo ""
echo "========================================"
echo "Video Downloader & Music Remover"
echo "========================================"
echo ""
echo "Checking Python installation..."

if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 not found!"
    echo ""
    echo "Install with: brew install python3 (macOS) or sudo apt install python3 (Linux)"
    echo ""
    exit 1
fi

python3 --version
echo "✓ Python found"
echo ""
echo "Installing/updating dependencies..."
pip3 install -r requirements.txt --quiet
echo "✓ Dependencies ready"
echo ""
echo "Starting application..."
echo ""

python3 -m src.main
