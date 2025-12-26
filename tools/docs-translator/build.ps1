# Build script for docs-translator executable on Windows
# Usage: .\build.ps1

$ErrorActionPreference = "Stop"

Write-Host "Building docs-translator executable..." -ForegroundColor Cyan

# Check if conda is activated
$condaEnv = $env:CONDA_DEFAULT_ENV
if (-not $condaEnv) {
    Write-Host "Conda environment not activated. Activating docs-translator environment..." -ForegroundColor Yellow
    # Initialize conda for PowerShell
    & "C:\ProgramData\miniconda3\Scripts\conda.exe" init powershell
    & "C:\ProgramData\miniconda3\Scripts\activate.bat" docs-translator
}

# Install build dependencies
Write-Host "Installing build dependencies..." -ForegroundColor Cyan
pip install -e ".[build]"

# Create build directory if it doesn't exist
if (-not (Test-Path "build")) {
    New-Item -ItemType Directory -Path "build" | Out-Null
}

# Build executable
Write-Host "Running PyInstaller..." -ForegroundColor Cyan
pyinstaller `
    --onefile `
    --windowed `
    --name "docs-translator" `
    --distpath "./dist" `
    --buildpath "./build" `
    --specpath "./build" `
    --add-data "docs_translator:docs_translator" `
    --console `
    docs_translator/cli/main.py

# Check if build was successful
if ($LASTEXITCODE -eq 0) {
    Write-Host "Build completed successfully!" -ForegroundColor Green
    Write-Host "Executable location: ./dist/docs-translator.exe" -ForegroundColor Green
    Write-Host ""
    Write-Host "To use it:" -ForegroundColor Cyan
    Write-Host "  1. Copy ./dist/docs-translator.exe to your desired location" -ForegroundColor White
    Write-Host "  2. Add the executable directory to your PATH (optional)" -ForegroundColor White
    Write-Host "  3. Run: docs-translator --help" -ForegroundColor White
} else {
    Write-Host "Build failed with error code $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
}
