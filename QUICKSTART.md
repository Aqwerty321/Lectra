# LECTRA v2.0 Quick Start 🚀

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies (2 minutes)
```powershell
# Run the automated setup script
.\setup-v2.ps1
```

This will:
- ✅ Check Python installation
- ✅ Install Python packages (PyPDF2, chromadb, etc.)
- ✅ Check Ollama and pull `nomic-embed-text`
- ✅ Verify FFmpeg installation
- ✅ Install Node dependencies

### Step 2: Start LECTRA (10 seconds)
```powershell
.\launch.ps1
```

This starts:
- Python sidecar (API server on port 8765)
- Vue frontend (Tauri desktop app)

### Step 3: Try the New Features! (3 minutes)

#### 📤 Upload a Document

1. Click **"📚 Notebook"** in the navbar
2. Stay on the **"📤 Upload"** tab
3. Enter project name: `test-lecture`
4. Click file selector, choose a PDF or DOCX
5. Click **"🚀 Upload & Process"**
6. Wait 10-30 seconds
7. See topics extracted from your document!

#### 🎬 Generate Presentation

1. Click **"🎬 Generate"** tab
2. Select your collection from dropdown
3. Enter a topic/query (e.g., "Introduction" or "Chapter 1")
4. Choose language (English/Hindi) and voice
5. Ensure "Generate video" is checked
6. Click **"✨ Generate Presentation"**
7. Wait 30-60 seconds
8. See result with:
   - Number of slides created
   - Total duration
   - Number of chunks retrieved (RAG)
   - Video ready notification

#### 📺 Watch Video

1. Click **"📺 Viewer"** tab
2. Select `test-lecture` from dropdown
3. Video loads automatically
4. Play with native controls!
5. Notice subtitles embedded in video 🎉

## 🎯 What Just Happened?

### Upload Phase
```
Your PDF/DOCX 
   → Text extraction (PyPDF2/python-docx)
   → Smart chunking (1000 chars with 200 overlap)
   → Ollama embeddings (nomic-embed-text)
   → ChromaDB storage
   → Topic detection
```

### Generation Phase
```
Your Topic Query
   → Embedding generation
   → Vector search (top 10 relevant chunks)
   → Context injection to LLM
   → Outline creation
   → Slide generation with images
   → TTS synthesis with prosody
   → Video assembly with subtitles
   → 🎬 Final MP4!
```

## 📚 Original Quick Start (v1.0)

## Immediate Next Steps (Copy-Paste Ready)

### 1️⃣ Install Python Dependencies

```powershell
cd C:\edgettstest\LECTRA\sidecar
pip install -r requirements.txt
```

### 2️⃣ Build Sidecar Executable

```powershell
cd C:\edgettstest\LECTRA
.\scripts\build_sidecar.ps1
```

### 3️⃣ Setup UI

```powershell
cd C:\edgettstest\LECTRA\ui
npm install
```

### 4️⃣ Add Image Assets

**REQUIRED**: Place these 4 images in `ui\src\assets\images\`:
- `darkest_wood.png` (navbar background)
- `dark_wood.png` (hero background)  
- `light_wood.png` (content background)
- `title.png` (LECTRA logo)

**Where to get them**:
- Create seamless wood textures (128x128px tiles)
- Or use solid colors temporarily
- Or download from free texture sites like [Toptal Subtle Patterns](https://www.toptal.com/designers/subtlepatterns/)

### 5️⃣ Start Ollama (if not running)

```powershell
# Check if Ollama is running
curl http://127.0.0.1:11434/api/tags

# If not running, start it
ollama serve

# In another terminal, verify model exists
ollama list
# Should show: llama3.1:latest

# If model not found, pull it
ollama pull llama3.1:latest
```

### 6️⃣ Run in Dev Mode

```powershell
cd C:\edgettstest\LECTRA\ui
npm run tauri dev
```

This will:
- ✅ Start Vite dev server
- ✅ Launch Tauri app window
- ✅ Auto-start Python sidecar
- ✅ Open the app ready to use

## Quick Test

Once the app is running:

1. **Click "Generate (English)"** button
2. **Project name**: `test-lecture`
3. **Click "Use Big Sample (EN)"**
4. **Click "Generate Audio"**
5. Wait ~30-60 seconds
6. **Check output**: `C:\Users\<YourName>\Lectures\test-lecture\`
   - `audio.mp3` - Your generated audio! 🎉
   - `tagged.txt` - Text with nuance tags
   - `timings.json` - Per-sentence timing data

## Minimal Setup (No Images)

If you don't have wood textures yet:

1. **Remove image references** from `ui\src\styles.css`:
   ```css
   /* Comment out these lines temporarily */
   /*
   .bg-darkest-wood {
     background: url('./assets/images/darkest_wood.png') repeat;
   }
   */
   
   /* Replace with solid colors */
   .bg-darkest-wood { background: #2d2d2d; }
   .bg-dark-wood { background: #3d3d3d; }
   .bg-light-wood { background: #f5f5f5; }
   ```

2. **Hide logo** in `ui\src\components\HeroLogo.vue`:
   ```vue
   <!-- Comment out the img tag -->
   <!-- <img src="../assets/images/title.png" ... /> -->
   
   <!-- Add text logo instead -->
   <h1 class="text-6xl font-bold text-white mb-8">LECTRA</h1>
   ```

3. **Restart dev server** and it will work!

## Testing Without UI (API Only)

If you just want to test the backend:

```powershell
# Start sidecar
cd C:\edgettstest\LECTRA\sidecar
python -m app.api

# In another terminal, test it
$body = @{
    project = "api-test"
    use_sample = "en"
    lang = "en"
    fallback_rate = "-10%"
    fallback_pitch = "+0st"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/generate" -Method POST -Body $body -ContentType "application/json"

# Check output
ls ~\Lectures\api-test\
```

## Common First-Run Issues

### ❌ "Ollama not reachable"
```powershell
# Start Ollama
ollama serve

# Verify it's running
curl http://127.0.0.1:11434/api/tags
```

### ❌ "Cannot find module 'vue'"
```powershell
cd ui
Remove-Item -Recurse node_modules
npm install
```

### ❌ "PyInstaller not found"
```powershell
pip install pyinstaller
cd C:\edgettstest\LECTRA
.\scripts\build_sidecar.ps1
```

### ❌ "EdgeTTS failed (502)"
- Check internet connection (needed for first voice download)
- Try "Estimate Only" button instead (skips audio)

### ❌ Images not loading
- See "Minimal Setup" above to use solid colors
- Or add placeholder images to `ui\src\assets\images\`

## Full Documentation

- **Main README**: `C:\edgettstest\LECTRA\README.md`
- **Setup Guide**: `C:\edgettstest\LECTRA\SETUP.md`
- **Sidecar API**: Check FastAPI docs at http://127.0.0.1:8765/docs when running

## What You Get

After following these steps, you'll have a **fully functional desktop app** that:

✅ Takes raw text → Adds AI nuance tags → Generates natural speech  
✅ Works with English & Hindi  
✅ Estimates timing without audio (fast preview)  
✅ Outputs MP3, timing JSON, VTT subtitles, and SSML  
✅ No terminal needed - all in beautiful wood-themed UI  
✅ Offline-capable (after initial setup)

---

**Need Help?** Check `SETUP.md` for detailed troubleshooting.

**Ready to ship?** Run `npm run tauri build` to create an installer!

🎉 **You're all set! Start generating natural lectures!** 🎙️
