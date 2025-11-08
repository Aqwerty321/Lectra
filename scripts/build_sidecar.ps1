# LECTRA Sidecar - PyInstaller Build Script
# Bundles FastAPI server into single executable

Write-Host "Building LECTRA sidecar..." -ForegroundColor Cyan

# Check if PyInstaller is installed
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    Write-Host "PyInstaller not found. Installing..." -ForegroundColor Yellow
    pip install pyinstaller
}

# Navigate to sidecar directory
Push-Location "$PSScriptRoot\..\sidecar"

# Build with PyInstaller
Write-Host "Running PyInstaller..." -ForegroundColor Green

pyinstaller `
    --name lecture-sidecar `
    --onefile `
    --hidden-import=uvicorn.logging `
    --hidden-import=uvicorn.loops `
    --hidden-import=uvicorn.loops.auto `
    --hidden-import=uvicorn.protocols `
    --hidden-import=uvicorn.protocols.http `
    --hidden-import=uvicorn.protocols.http.auto `
    --hidden-import=uvicorn.protocols.websockets `
    --hidden-import=uvicorn.protocols.websockets.auto `
    --hidden-import=uvicorn.lifespan `
    --hidden-import=uvicorn.lifespan.on `
    --add-data "app\services\nuance_system_prompt.txt;app\services" `
    --collect-all edge_tts `
    launcher.py

# Move to bin directory
Write-Host "Moving executable to bin..." -ForegroundColor Green
$binDir = "..\bin"
if (-not (Test-Path $binDir)) {
    New-Item -ItemType Directory -Path $binDir | Out-Null
}

Copy-Item "dist\lecture-sidecar.exe" "$binDir\lecture-sidecar.exe" -Force

Write-Host "Build complete: bin\lecture-sidecar.exe" -ForegroundColor Green
Write-Host "Test with: .\bin\lecture-sidecar.exe --port 8765" -ForegroundColor Cyan

Pop-Location
