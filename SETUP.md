# LECTRA Development Setup Guide

## 🎯 Complete Setup Instructions

### Prerequisites

1. **Python 3.11+** - For FastAPI sidecar
   ```powershell
   python --version  # Should be 3.11 or higher
   ```

2. **Node.js 18+** - For Vue UI
   ```powershell
   node --version
   npm --version
   ```

3. **Rust** - For Tauri desktop app
   ```powershell
   # Install from https://rustup.rs/
   rustc --version
   cargo --version
   ```

4. **Ollama** - Local LLM inference
   ```powershell
   # Download from https://ollama.ai/
   ollama --version
   
   # Pull the model
   ollama pull llama3.1:latest
   
   # Start Ollama (should auto-start on Windows)
   # Or run: ollama serve
   ```

5. **PostgreSQL** (Optional) - For job logging
   ```powershell
   # Install from https://www.postgresql.org/download/windows/
   # Create database: lectra
   # Update .env with connection string
   ```

6. **FFmpeg** - For audio processing
   ```powershell
   # Download from https://ffmpeg.org/download.html
   # Extract to C:\ffmpeg\
   # Verify: C:\ffmpeg\bin\ffmpeg.exe should exist
   ```

### Step 1: Clone and Configure

```powershell
cd C:\edgettstest\LECTRA

# Copy environment template
Copy-Item .env.example .env

# Edit .env with your settings (if needed)
# notepad .env
```

### Step 2: Build Python Sidecar

```powershell
# Install Python dependencies
cd sidecar
pip install -r requirements.txt

# Test sidecar manually (optional)
python -m app.api
# Should start on http://127.0.0.1:8000
# Press Ctrl+C to stop

# Build standalone executable
cd ..
.\scripts\build_sidecar.ps1

# Verify: bin\lecture-sidecar.exe should exist
```

### Step 3: Setup UI

```powershell
cd ui

# Install Node dependencies
npm install

# Install Tauri CLI (if not already installed)
npm install -D @tauri-apps/cli
```

### Step 4: Add Image Assets

Place these images in `ui\src\assets\images\`:

- **darkest_wood.png** - Seamless texture for navbar (dark brown wood)
- **dark_wood.png** - Seamless texture for hero section (medium brown)
- **light_wood.png** - Seamless texture for content sections (light brown)
- **title.png** - LECTRA logo/title image (transparent PNG)

> **Note**: If you don't have these images, the app will still work but backgrounds will be transparent.

### Step 5: Generate Tauri Icons (Optional)

```powershell
cd ui

# If you have a 512x512 PNG icon:
npm run tauri icon path\to\your\icon.png

# This generates all required icon sizes in src-tauri\icons\
```

## 🚀 Running the App

### Development Mode

```powershell
cd C:\edgettstest\LECTRA\ui

# Start both UI and sidecar in dev mode
npm run tauri dev
```

This will:
1. Start Vite dev server (UI hot reload)
2. Launch Tauri window
3. Auto-start Python sidecar
4. Open app in development window

### Production Build

```powershell
cd C:\edgettstest\LECTRA\ui

# Build the installer
npm run tauri build
```

Outputs:
- **Installer**: `ui\src-tauri\target\release\bundle\nsis\LECTRA_1.0.0_x64-setup.exe` (Windows)
- **Portable**: `ui\src-tauri\target\release\lectra.exe`

## 🧪 Testing the Sidecar Independently

```powershell
# Option 1: Run Python directly
cd sidecar
python -m app.api

# Option 2: Run built executable
cd ..
.\bin\lecture-sidecar.exe --port 8765

# Test health check
curl http://127.0.0.1:8765/healthz
# Should return: {"status":"ok","service":"lectra-sidecar"}

# Test generation (PowerShell)
$body = @{
    project = "test-run"
    text = ""
    lang = "en"
    use_sample = "en"
    fallback_rate = "-10%"
    fallback_pitch = "+0st"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8765/generate" -Method POST -Body $body -ContentType "application/json"
```

## 📂 Project Structure Reference

```
LECTRA/
├── .env.example              # Environment template
├── README.md                 # Main documentation
├── tauri.conf.json           # Tauri configuration
├── sidecar/                  # Python FastAPI backend
│   ├── app/
│   │   ├── config.py         # Config loader
│   │   ├── api.py            # FastAPI routes
│   │   └── services/
│   │       ├── ollama_client.py
│   │       ├── tagging.py
│   │       ├── tag_to_ssml.py
│   │       ├── tts_engine.py
│   │       ├── timing.py
│   │       ├── postgres.py
│   │       ├── ppt_sync.py
│   │       ├── samples.py
│   │       └── nuance_system_prompt.txt
│   └── requirements.txt
├── scripts/
│   └── build_sidecar.ps1     # PyInstaller build script
├── bin/
│   └── lecture-sidecar.exe   # (Generated)
└── ui/                       # Vue 3 + Tailwind frontend
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.cjs
    ├── index.html
    ├── src/
    │   ├── main.ts
    │   ├── App.vue
    │   ├── styles.css
    │   ├── assets/images/
    │   └── components/
    │       ├── NavBar.vue
    │       ├── HeroLogo.vue
    │       ├── FeatureCards.vue
    │       ├── TechStack.vue
    │       ├── GeneratorPanel.vue
    │       ├── ProgressBar.vue
    │       └── FooterMadeWithLove.vue
    └── src-tauri/            # Rust Tauri app
        ├── Cargo.toml
        ├── src/main.rs
        └── icons/
```

## 🐛 Troubleshooting

### Sidecar won't start
- Check Ollama is running: `ollama list`
- Verify Python dependencies: `pip list | grep -E "fastapi|edge-tts"`
- Check port 8765 is free: `netstat -ano | findstr :8765`

### "Ollama not reachable" error
```powershell
# Start Ollama
ollama serve

# In another terminal, verify model exists
ollama list
# Should show llama3.1:latest

# If not, pull it
ollama pull llama3.1:latest
```

### EdgeTTS fails (502 error)
- Check internet connection (EdgeTTS requires internet for first voice download)
- Use "Estimate Only" mode to skip audio generation
- Verify FFmpeg: `C:\ffmpeg\bin\ffmpeg.exe -version`

### UI build errors
```powershell
cd ui

# Clear node_modules and reinstall
Remove-Item -Recurse -Force node_modules
npm install

# Clear Vite cache
Remove-Item -Recurse -Force dist
npm run build
```

### Database errors (optional)
- If PostgreSQL not installed, app still works (logging disabled)
- Check DATABASE_URL in .env matches your Postgres setup
- Ensure database `lectra` exists

## 📝 Usage Examples

### Generate English Lecture Audio

1. Launch LECTRA app
2. Click "Generate (English)" button
3. Enter project name: `ml-intro`
4. Select "Use Big Sample (EN)"
5. Choose voice (or keep default)
6. Click "Generate Audio"
7. Wait 30-60 seconds
8. Check output: `C:\Users\<you>\Lectures\ml-intro\`
   - `tagged.txt` - Tagged text
   - `ssml.xml` - SSML markup
   - `audio.mp3` - Final audio
   - `timings.json` - Per-sentence timing
   - `subs.vtt` - WebVTT subtitles

### Estimate Timing Without Audio

1. Same setup as above
2. Click "Estimate Only" instead
3. Gets timing data in ~10 seconds (no audio generated)
4. Useful for quick previews

### Hindi Lecture

1. Click "Generate (हिंदी)" or select Hindi language
2. Voice auto-defaults to `hi-IN-SwaraNeural`
3. Use Hindi sample or paste Devanagari text
4. Generate as normal

## 🎓 Next Steps

- **Add more samples**: Edit `sidecar/app/services/samples.py`
- **Customize system prompt**: Edit `sidecar/app/services/nuance_system_prompt.txt`
- **Add voices**: Update `GeneratorPanel.vue` voice dropdown
- **Implement PPT sync**: Complete `sidecar/app/services/ppt_sync.py`

## 📦 Distribution

After building, you can distribute:

1. **Installer** (recommended): Share the `.exe` from `bundle\nsis\`
2. **Portable**: Share the standalone `.exe` from `target\release\`

Users will need:
- Ollama installed with llama3.1:latest
- FFmpeg at `C:\ffmpeg\bin\` (or in PATH)
- Internet for first-time EdgeTTS voice download

---

**Happy Lecturing! 🎙️**

*Made with ❤️ by Team Just-Git-Gud*
