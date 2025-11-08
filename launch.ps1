# LECTRA Launch Script
Write-Host "Launching LECTRA..." -ForegroundColor Cyan

# Refresh PATH to include Rust
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Change to UI directory
Set-Location C:\edgettstest\LECTRA\ui

# Launch Tauri dev
Write-Host "Starting Tauri dev server (first build takes 2-3 minutes)..." -ForegroundColor Yellow
npm run tauri dev
