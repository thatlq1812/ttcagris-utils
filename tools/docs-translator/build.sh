#!/bin/bash
# Build script for docs-translator executable on Windows (Git Bash)
# Usage: bash build.sh

set -e

echo "Building docs-translator executable..."

# Source bashrc to ensure conda is initialized
source ~/.bashrc

# Activate docs-translator environment
conda activate docs-translator || {
    echo "Error: docs-translator conda environment not found"
    echo "Creating environment..."
    conda create -n docs-translator python=3.11 -y
    conda activate docs-translator
}

# Install build dependencies
echo "Installing build dependencies..."
pip install -e ".[build]"

# Create build directory if it doesn't exist
mkdir -p build

# Build executable
echo "Running PyInstaller..."
pyinstaller \
    --onefile \
    --name "docs-translator" \
    --distpath "./dist" \
    --buildpath "./build" \
    --specpath "./build" \
    --add-data "docs_translator:docs_translator" \
    --console \
    docs_translator/cli/main.py

echo ""
echo "Build completed successfully!"
echo "Executable location: ./dist/docs-translator.exe"
echo ""
echo "To use it:"
echo "  1. Copy ./dist/docs-translator.exe to your desired location"
echo "  2. Add the executable directory to your PATH (optional)"
echo "  3. Run: docs-translator --help"
