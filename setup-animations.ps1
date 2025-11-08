# LECTRA Interactive Animations - Quick Setup Script
# Run this from the LECTRA root directory

Write-Host "🎭 LECTRA Interactive Animations Setup" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "ui\package.json")) {
    Write-Host "❌ Error: Please run this script from the LECTRA root directory" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Found LECTRA project" -ForegroundColor Green
Write-Host ""

# Step 1: Install GSAP
Write-Host "📦 Step 1: Installing GSAP (GreenSock Animation Platform)..." -ForegroundColor Yellow
Set-Location ui

try {
    npm install gsap
    Write-Host "✅ GSAP installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install GSAP. Please install manually:" -ForegroundColor Red
    Write-Host "   cd ui && npm install gsap" -ForegroundColor Yellow
}

Set-Location ..
Write-Host ""

# Step 2: Check Python dependencies
Write-Host "🐍 Step 2: Checking Python dependencies..." -ForegroundColor Yellow
Set-Location sidecar

$pythonCheck = python -c "import requests; import json; print('OK')" 2>$null
if ($pythonCheck -eq "OK") {
    Write-Host "✅ Python dependencies OK" -ForegroundColor Green
} else {
    Write-Host "⚠️  Some Python dependencies may be missing" -ForegroundColor Yellow
    Write-Host "   Run: pip install -r requirements.txt" -ForegroundColor Yellow
}

Set-Location ..
Write-Host ""

# Step 3: Check Ollama
Write-Host "🦙 Step 3: Checking Ollama..." -ForegroundColor Yellow
try {
    $ollamaCheck = Invoke-WebRequest -Uri "http://127.0.0.1:11434/api/tags" -Method GET -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✅ Ollama is running" -ForegroundColor Green
    
    # Check for llama3.2:3b model
    $models = ($ollamaCheck.Content | ConvertFrom-Json).models
    $hasModel = $models | Where-Object { $_.name -like "llama3.2:3b*" }
    
    if ($hasModel) {
        Write-Host "✅ llama3.2:3b model found" -ForegroundColor Green
    } else {
        Write-Host "⚠️  llama3.2:3b model not found" -ForegroundColor Yellow
        Write-Host "   Run: ollama pull llama3.2:3b" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Ollama is not running or not accessible" -ForegroundColor Red
    Write-Host "   Please start Ollama: ollama serve" -ForegroundColor Yellow
}

Write-Host ""

# Step 4: Create sample animations test
Write-Host "📝 Step 4: Creating test files..." -ForegroundColor Yellow

$testAnimations = @"
{
  "slides": [
    {
      "slide_number": 1,
      "start_time": 0.0,
      "end_time": 4.0,
      "steps": [
        {
          "id": 1,
          "text": "Welcome to Interactive Learning!",
          "action": "fadeIn",
          "duration": 2.0,
          "hint": "This is a sample animated lecture",
          "element": "title"
        }
      ]
    }
  ]
}
"@

$testDir = "$env:USERPROFILE\Lectures\test-interactive"
if (-not (Test-Path $testDir)) {
    New-Item -Path $testDir -ItemType Directory -Force | Out-Null
}

$testAnimations | Out-File -FilePath "$testDir\animations.json" -Encoding UTF8
Write-Host "✅ Test animations created in $testDir" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "🎉 Setup Complete!" -ForegroundColor Green
Write-Host "==================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Start the backend: cd sidecar && python -m uvicorn app.api:app --host 127.0.0.1 --port 8765" -ForegroundColor White
Write-Host "   2. Start the frontend: cd ui && npm run tauri:dev" -ForegroundColor White
Write-Host "   3. Navigate to the 🎭 Interactive tab" -ForegroundColor White
Write-Host "   4. Generate a new lecture to see animations!" -ForegroundColor White
Write-Host ""
Write-Host "📖 Documentation: See INTERACTIVE_ANIMATIONS_GUIDE.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "✨ Happy Learning! ✨" -ForegroundColor Magenta
