# LECTRA v2.0 Setup Script

Write-Host "SETUP: LECTRA v2.0 - Document Notebook Setup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "CHECK: Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "OK: Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "ERROR: Python not found! Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Install Python dependencies
Write-Host ""
Write-Host "INSTALL: Installing Python dependencies..." -ForegroundColor Yellow
Push-Location sidecar
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "OK: Python dependencies installed" -ForegroundColor Green
} else {
    Write-Host "ERROR: Failed to install Python dependencies" -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location

# Check Ollama
Write-Host ""
Write-Host "CHECK: Checking Ollama..." -ForegroundColor Yellow
$ollamaVersion = ollama --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "OK: Ollama found: $ollamaVersion" -ForegroundColor Green
    
    # Pull embedding model
    Write-Host "INSTALL: Pulling nomic-embed-text model..." -ForegroundColor Yellow
    ollama pull nomic-embed-text
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK: Embedding model ready" -ForegroundColor Green
    } else {
        Write-Host "WARN: Failed to pull embedding model" -ForegroundColor Yellow
    }
} else {
    Write-Host "WARN: Ollama not found. Install from: https://ollama.ai" -ForegroundColor Yellow
}

# Check FFmpeg
Write-Host ""
Write-Host "CHECK: Checking FFmpeg..." -ForegroundColor Yellow
$ffmpegVersion = ffmpeg -version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "OK: FFmpeg found" -ForegroundColor Green
} else {
    Write-Host "WARN: FFmpeg not found" -ForegroundColor Yellow
    Write-Host "   Checking C:\ffmpeg\bin..." -ForegroundColor Gray
    if (Test-Path "C:\ffmpeg\bin\ffmpeg.exe") {
        Write-Host "OK: FFmpeg found at C:\ffmpeg\bin" -ForegroundColor Green
    } else {
        Write-Host "ERROR: FFmpeg not found" -ForegroundColor Red
        Write-Host "   Download from: https://ffmpeg.org/download.html" -ForegroundColor Yellow
        Write-Host "   Extract to: C:\ffmpeg" -ForegroundColor Yellow
    }
}

# Install Node dependencies (if needed)
Write-Host ""
Write-Host "CHECK: Checking frontend..." -ForegroundColor Yellow
if (Test-Path "ui/package.json") {
    Push-Location ui
    if (-not (Test-Path "node_modules")) {
        Write-Host "INSTALL: Installing Node dependencies..." -ForegroundColor Yellow
        npm install
        if ($LASTEXITCODE -eq 0) {
            Write-Host "OK: Node dependencies installed" -ForegroundColor Green
        } else {
            Write-Host "ERROR: Failed to install Node dependencies" -ForegroundColor Red
        }
    } else {
        Write-Host "OK: Node dependencies already installed" -ForegroundColor Green
    }
    Pop-Location
}

# Summary
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "SUCCESS: Setup Complete!" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start LECTRA:" -ForegroundColor Green
Write-Host "   .\launch.ps1" -ForegroundColor White
Write-Host ""
Write-Host "New Features:" -ForegroundColor Green
Write-Host "   - PDF/DOCX upload and processing" -ForegroundColor White
Write-Host "   - Vector database (ChromaDB)" -ForegroundColor White
Write-Host "   - RAG-powered generation" -ForegroundColor White
Write-Host "   - In-app video player" -ForegroundColor White
Write-Host "   - Subtitle embedding" -ForegroundColor White
Write-Host ""
Write-Host "Read NOTEBOOK_FEATURES.md for full documentation" -ForegroundColor Yellow
Write-Host ""
