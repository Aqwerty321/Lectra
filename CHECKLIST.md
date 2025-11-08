# ✅ LECTRA Setup Checklist

## Before You Start

- [ ] **Ollama is installed** and running
  ```powershell
  ollama --version
  curl http://127.0.0.1:11434/api/tags
  ```

- [ ] **llama3.1:latest is pulled**
  ```powershell
  ollama list  # Should show llama3.1:latest
  # If not: ollama pull llama3.1:latest
  ```

- [ ] **Python 3.11+** is installed
  ```powershell
  python --version  # Should be 3.11 or higher
  ```

- [ ] **Node.js 18+** is installed
  ```powershell
  node --version
  npm --version
  ```

- [ ] **Rust** is installed (for Tauri build)
  ```powershell
  rustc --version
  cargo --version
  # If not: https://rustup.rs/
  ```

- [ ] **FFmpeg** is at `C:\ffmpeg\bin\ffmpeg.exe`
  ```powershell
  C:\ffmpeg\bin\ffmpeg.exe -version
  # If not: https://ffmpeg.org/download.html
  ```

---

## Step 1: Python Sidecar Setup

- [ ] Navigate to sidecar directory
  ```powershell
  cd C:\edgettstest\LECTRA\sidecar
  ```

- [ ] Install Python dependencies
  ```powershell
  pip install -r requirements.txt
  ```
  
  Expected packages:
  - fastapi
  - uvicorn
  - edge-tts
  - requests
  - pydub
  - python-dotenv
  - psycopg (if using PostgreSQL)

- [ ] Test sidecar manually (optional)
  ```powershell
  python -m app.api
  # Should start on http://127.0.0.1:8000
  # Press Ctrl+C to stop
  ```

- [ ] Build sidecar executable
  ```powershell
  cd C:\edgettstest\LECTRA
  .\scripts\build_sidecar.ps1
  ```

- [ ] Verify executable exists
  ```powershell
  Test-Path .\bin\lecture-sidecar.exe  # Should return True
  ```

---

## Step 2: UI Setup

- [ ] Navigate to UI directory
  ```powershell
  cd C:\edgettstest\LECTRA\ui
  ```

- [ ] Install Node dependencies
  ```powershell
  npm install
  ```
  
  This installs:
  - Vue 3
  - Tailwind CSS
  - Vite
  - Tauri CLI
  - Other dependencies

- [ ] Wait for installation to complete (~2-5 minutes)

---

## Step 3: Image Assets (REQUIRED)

Choose **Option A** (proper images) or **Option B** (quick workaround):

### Option A: Add Real Images ✨ (Recommended)

- [ ] Create/download these 4 images:
  1. **darkest_wood.png** - Dark brown wood texture (128x128px)
  2. **dark_wood.png** - Medium brown wood texture (128x128px)
  3. **light_wood.png** - Light brown/beige wood texture (128x128px)
  4. **title.png** - LECTRA logo text (transparent PNG, ~800x200px)

- [ ] Place all 4 images in:
  ```
  C:\edgettstest\LECTRA\ui\src\assets\images\
  ```

- [ ] Verify images exist:
  ```powershell
  ls C:\edgettstest\LECTRA\ui\src\assets\images\
  # Should show all 4 PNG files
  ```

### Option B: Use Solid Colors 🎨 (Quick Workaround)

- [ ] Edit `ui\src\styles.css` and replace wood backgrounds:
  ```css
  /* Around line 26-34, replace: */
  .bg-darkest-wood {
    background: #2d2d2d;  /* Dark gray instead of texture */
  }

  .bg-dark-wood {
    background: #3d3d3d;  /* Medium gray instead of texture */
  }

  .bg-light-wood {
    background: #f5f5f5;  /* Light gray instead of texture */
  }
  ```

- [ ] Edit `ui\src\components\HeroLogo.vue` and replace logo:
  ```vue
  <!-- Around line 3-7, replace <img> tag with: -->
  <h1 class="text-6xl font-bold text-white mb-8">LECTRA</h1>
  ```

---

## Step 4: Configuration (Optional)

- [ ] Copy environment template
  ```powershell
  cd C:\edgettstest\LECTRA
  Copy-Item .env.example .env
  ```

- [ ] Edit `.env` if needed (default values usually work)
  ```env
  OLLAMA_URL=http://127.0.0.1:11434         # ✅ Usually correct
  DATABASE_URL=postgres://...                # ❌ Only if using Postgres
  OUTPUT_ROOT=~/Lectures                     # ✅ Default is fine
  FFMPEG_BIN=C:\ffmpeg\bin\ffmpeg.exe       # ✅ Check this path
  DEFAULT_EN_VOICE=en-US-GuyNeural          # ✅ Default is fine
  DEFAULT_HI_VOICE=hi-IN-SwaraNeural        # ✅ Default is fine
  ```

---

## Step 5: First Run 🚀

- [ ] Make sure Ollama is running
  ```powershell
  # In a separate terminal if needed:
  ollama serve
  ```

- [ ] Start the app in dev mode
  ```powershell
  cd C:\edgettstest\LECTRA\ui
  npm run tauri dev
  ```

- [ ] Wait for:
  - Vite dev server to start (~10 seconds)
  - Tauri window to open (~5 seconds)
  - Sidecar to auto-start and report "ready" (~5 seconds)

- [ ] You should see:
  - Desktop window with LECTRA UI
  - Wood-themed design (or solid colors if using Option B)
  - Status message: "Sidecar ready!" (green toast)

---

## Step 6: First Test 🧪

- [ ] Click **"Generate (English)"** button in hero section

- [ ] In the generator panel:
  - [ ] Project name: `test-lecture`
  - [ ] Language: **English** (should be pre-selected)
  - [ ] Click **"Use Big Sample (EN)"** button
  - [ ] Leave voice as default or select **en-US-GuyNeural**

- [ ] Click **"Generate Audio"** button

- [ ] Wait 30-60 seconds for processing
  - Progress bar should appear
  - Watch console for segment processing

- [ ] Check for success ✅:
  - Green success banner appears
  - Duration shown (~120-150 seconds)
  - Sentence count shown (~26 sentences)
  - Output paths displayed

- [ ] Verify output files exist:
  ```powershell
  ls ~\Lectures\test-lecture\
  ```
  
  Should contain:
  - [ ] `tagged.txt` - Tagged text with prosody markers
  - [ ] `ssml.xml` - SSML markup (reference)
  - [ ] `audio.mp3` - **Generated audio!** 🎉
  - [ ] `timings.json` - Per-sentence timing data
  - [ ] `subs.vtt` - WebVTT subtitles

- [ ] Listen to the audio:
  ```powershell
  # In PowerShell (opens default media player)
  Invoke-Item ~\Lectures\test-lecture\audio.mp3
  ```

---

## Step 7: Second Test (Hindi) 🇮🇳

- [ ] Click **"Generate (हिंदी)"** button

- [ ] In the generator panel:
  - [ ] Project name: `hindi-test`
  - [ ] Language: **हिंदी** (should be pre-selected)
  - [ ] Click **"Use Big Sample (HI)"** button
  - [ ] Voice should default to **hi-IN-SwaraNeural**

- [ ] Click **"Generate Audio"**

- [ ] Wait ~30-60 seconds

- [ ] Verify Hindi audio generated:
  ```powershell
  ls ~\Lectures\hindi-test\
  # Should contain all 5 output files
  
  Invoke-Item ~\Lectures\hindi-test\audio.mp3
  # Should hear Hindi speech
  ```

---

## Step 8: Test Estimate Mode ⚡

- [ ] Clear project name and enter: `timing-test`

- [ ] Keep English, use big sample

- [ ] Click **"Estimate Only"** (NOT "Generate Audio")

- [ ] Should complete in ~5-10 seconds (much faster!)

- [ ] Verify only timing files created:
  ```powershell
  ls ~\Lectures\timing-test\
  # Should have: tagged.txt, timings.json, subs.vtt
  # Should NOT have: audio.mp3
  ```

---

## Troubleshooting Common Issues

### ❌ Sidecar won't start

- [ ] Check Python version: `python --version` (need 3.11+)
- [ ] Reinstall dependencies: 
  ```powershell
  cd C:\edgettstest\LECTRA\sidecar
  pip install --force-reinstall -r requirements.txt
  ```
- [ ] Check port 8765 is free:
  ```powershell
  netstat -ano | findstr :8765
  # Should be empty. If not, kill that process.
  ```

### ❌ "Ollama not reachable"

- [ ] Start Ollama:
  ```powershell
  ollama serve
  ```
- [ ] Verify it's running:
  ```powershell
  curl http://127.0.0.1:11434/api/tags
  ```
- [ ] Check model exists:
  ```powershell
  ollama list  # Should show llama3.1:latest
  ```

### ❌ "EdgeTTS failed (502)"

- [ ] Check internet connection (needed for first voice download)
- [ ] Try "Estimate Only" mode instead (skips audio)
- [ ] Verify FFmpeg:
  ```powershell
  C:\ffmpeg\bin\ffmpeg.exe -version
  ```

### ❌ UI won't load / blank window

- [ ] Check console for errors
- [ ] Verify images exist (or use Option B solid colors)
- [ ] Clear cache and rebuild:
  ```powershell
  cd C:\edgettstest\LECTRA\ui
  Remove-Item -Recurse -Force node_modules, dist
  npm install
  npm run tauri dev
  ```

### ❌ Build fails / compilation errors

- [ ] Update Rust:
  ```powershell
  rustup update
  ```
- [ ] Clear Cargo cache:
  ```powershell
  cd ui\src-tauri
  cargo clean
  cd ..\..
  npm run tauri dev
  ```

---

## Production Build Checklist 📦

Once everything works in dev mode:

- [ ] Ensure all tests pass (EN, HI, Estimate)

- [ ] Build sidecar if not already done:
  ```powershell
  .\scripts\build_sidecar.ps1
  ```

- [ ] Build Tauri installer:
  ```powershell
  cd ui
  npm run tauri build
  ```

- [ ] Wait 5-15 minutes for Rust compilation

- [ ] Find installer at:
  ```
  ui\src-tauri\target\release\bundle\nsis\LECTRA_1.0.0_x64-setup.exe
  ```

- [ ] Test installer on clean machine (optional)

---

## Final Verification ✅

- [ ] App launches without errors
- [ ] Sidecar auto-starts and reports healthy
- [ ] English sample generates audio successfully
- [ ] Hindi sample generates audio successfully
- [ ] Estimate mode works (timing without audio)
- [ ] Output files created in correct location
- [ ] Audio sounds natural with prosody variations
- [ ] Footer shows "Made with ❤️ by team Just-Git-Gud"

---

## 🎉 Success! What Next?

### Customization Ideas

- [ ] Edit system prompt: `sidecar\app\services\nuance_system_prompt.txt`
- [ ] Add more samples: `sidecar\app\services\samples.py`
- [ ] Change colors: `ui\src\styles.css` and `tailwind.config.cjs`
- [ ] Add more voices: `ui\src\components\GeneratorPanel.vue`
- [ ] Customize timing formula: `sidecar\app\services\timing.py`

### Distribution

- [ ] Share installer with users
- [ ] Write user guide with prerequisites (Ollama, FFmpeg)
- [ ] Create demo video showing the workflow

### Future Enhancements

- [ ] Implement PPT sync: `sidecar\app\services\ppt_sync.py`
- [ ] Add audio playback in-app (currently uses external player)
- [ ] Batch processing mode (multiple files)
- [ ] Web UI version (FastAPI + Vue without Tauri)
- [ ] Docker deployment

---

**Need help?** Check:
- `README.md` - Overview
- `SETUP.md` - Detailed setup guide
- `QUICKSTART.md` - Fast start instructions
- `PROJECT_SUMMARY.md` - Complete architecture explanation

**Ready to ship?** You now have a production-ready desktop app! 🚀

---

Made with ❤️ by GitHub Copilot for Team Just-Git-Gud
