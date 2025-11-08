# LECTRA - AI-Powered Lecture Generation System

> **Version 2.0** - Transform topics into engaging lectures with AI narration, interactive animations, quizzes, and multilingual support

---

## 📋 Quick Navigation

- [🚀 Quick Start](#-quick-start)
- [✨ Features](#-features)  
- [🎭 Interactive Animations](#-interactive-animations-where-to-find-them)
- [🎓 Quiz System](#-quiz-system)
- [🔧 Troubleshooting](#-troubleshooting)
- [🏗️ Architecture](#️-architecture)

---

## 🚀 Quick Start

### 1. Start Backend
```powershell
cd sidecar
python -m uvicorn app.api:app --host 127.0.0.1 --port 8765
```

### 2. Start Frontend
```powershell
cd ui
npm run tauri:dev
```

### 3. Generate a Lecture
1. Click **📚 Document Notebook**
2. Go to **🎬 Generate** tab
3. Enter topic: "Introduction to Photosynthesis"
4. Click **Generate Lecture**
5. Wait 50-70 seconds

### 4. View Interactive Animations
1. Click **🎭 Interactive** tab (NOT the Viewer tab!)
2. Select your lecture from dropdown
3. Click **Play** ▶
4. Use controls: **Next**, **Replay**, **Hint**

---

## ✨ Features

### 🎭 Two Viewing Modes

| Mode | Purpose | What You See |
|------|---------|--------------|
| **📺 Viewer** | Traditional video playback | Static MP4 with slides + voiceover |
| **🎭 Interactive** | Live animated learning | GSAP animations, step-by-step reveals, user controls |

**Important**: Animations are ONLY in the 🎭 Interactive tab, not in the video file!

### Core Capabilities
- 🎙️ **Natural AI Speech**: Microsoft Edge TTS with AI-powered prosody tagging
- 📊 **Auto-Generated Presentations**: Create PowerPoint slides from documents or topics
- 🎬 **Video Generation**: Synchronized video lectures with narration
- 📄 **Document Processing**: Support for PDF, DOCX, PPTX, and plain text
- 🌍 **Multilingual**: English and Hindi with multiple voice options
- ⚡ **RTX 5090 Optimized**: Sub-60-second generation time

### 🎓 Interactive Study Features
- **AI-Generated Quizzes**: Automatic MCQ generation using Ollama
- **Smart Video Pausing**: Quiz checkpoints at configurable intervals
- **Hints & Explanations**: Detailed feedback for every question
- **Progress Tracking**: Real-time scores, accuracy, and session analytics
- **Language-Aware**: Hindi PPT → Hindi quiz, English PPT → English quiz

---

## 🎭 Interactive Animations (WHERE TO FIND THEM!)

### ⚠️ Common Confusion

**"Where are the animations? I only see static slides!"**

The animations are **NOT in the video file**. They're in a completely separate interactive player.

### 📍 Step-by-Step Guide

1. **Generate a NEW lecture** (recent code has animation generation)
2. **Click the 🎭 Interactive tab** (next to 📺 Viewer tab)
3. **Select your lecture** from the dropdown menu
4. **Click Play** ▶ (big green button)
5. **Enjoy!** 🎉

### 🎮 Interactive Controls

- **▶️ Play/Pause**: Center green button - plays audio narration
- **⏭️ Next Step**: Orange button - advance to next animation step
- **🔁 Replay**: Blue button - replay current step
- **💡 Hint**: Purple button - show AI-generated hint for current step
- **⚡ Speed**: Dropdown to change narration speed (0.5x - 1.5x)
- **🖥️ Fullscreen**: Top-right button for immersive mode

### 🎨 Animation Types

The system uses GSAP (professional animation library) to create:

1. **fadeIn**: Content gradually appears
2. **slideIn**: Slides from the side with bounce effect
3. **highlight**: Background color flashes for emphasis
4. **pulse**: Element bounces to grab attention
5. **zoom**: Scales up from small to full size
6. **typewriter**: Text appears character-by-character
7. **draw**: Stroke animations for diagrams

### 🎯 What You'll See

```
┌─────────────────────────────────────────────┐
│  🎓 Interactive Lecture          [⛶]       │
│  Slide 1 of 8                              │
├─────────────────────────────────────────────┤
│                                             │
│        Gradient Background                  │
│                                             │
│        ✨ Title animates in                 │
│        ✨ Bullet point 1 slides in          │
│        ✨ Bullet point 2 slides in          │
│                                             │
│        💡 "This is a key concept!"          │
│        ━━━━━━━━━━━━━━━━━ 45%              │
│                                             │
├─────────────────────────────────────────────┤
│          🔁  ▶️  ⏭️  💡                     │
│       Replay Play Next Hint                 │
│                                             │
│       Speed: [1x ▼]                         │
└─────────────────────────────────────────────┘
```

### 🎬 How Animations are Generated

1. **During Lecture Generation** (backend):
   - After slide timings are calculated
   - Ollama (llama3.2:3b) analyzes each slide
   - Generates 3-6 animation steps per slide
   - Saves to `animations.json` in project folder

2. **During Playback** (frontend):
   - LecturePlayer loads: audio + timings + animations
   - Audio starts playing
   - GSAP triggers animations at precise timestamps
   - User can control pace with Next/Replay buttons

### 📁 File Structure

```
~/Lectures/{project-name}/
├── presentation_video.mp4    # Used by 📺 Viewer tab
├── narration.mp3              # Audio file
├── slide_timings.json         # Timestamp data
└── animations.json            # Animation steps (NEW!)
```

### 🔍 Verify Animations Were Generated

```powershell
# Check if animations.json exists
Get-ChildItem ~\Lectures\*\animations.json
```

If missing, regenerate the lecture with the latest code.

---

## 🎓 Quiz System

### Features

- **Smart Timing**: Quizzes appear at configurable slide intervals
- **Accurate Checkpoints**: Uses actual `slide_timings.json` (not approximations)
- **Language Detection**: Automatically generates Hindi or English questions
- **AI-Powered**: Ollama creates contextual MCQs with hints

### How to Use

1. Go to **🎓 Study Mode** tab
2. Select a lecture
3. Configure:
   - Quiz interval (e.g., every 3 slides)
   - Minimum questions per quiz
4. Watch video - it pauses automatically for quizzes
5. Answer questions, get instant feedback
6. See your progress and score

### Quiz Generation Process

```python
# Backend: api.py
1. Load slide content
2. Detect language from metadata
3. Call Ollama with language-specific prompt
4. Parse JSON response
5. Validate structure
6. Save quiz_data.json
```

### Troubleshooting Quizzes

**Issue**: "Quizzes not appearing at slide 3"
- **Fix**: Updated to use actual `slide_timings.json` timestamps

**Issue**: "Hindi PPT but English questions"
- **Fix**: Language detection from metadata, language-aware prompts

**Issue**: "Quiz appears too early/late"
- **Fix**: Added `/get_slide_timings` endpoint for precise timing

---

## 🔧 Troubleshooting

### Interactive Tab Issues

#### "I don't see the 🎭 Interactive tab!"

**Solution**:
- Restart the frontend: `Ctrl+C` then `npm run tauri:dev`
- Verify GSAP installed: `cd ui && npm list gsap`
- Should show: `gsap@3.13.0`

#### "Tab is there but window spills out of container"

**Solution**: Fixed in latest code
- Container height limited to `calc(100vh - 200px)`
- Control panel shrunk to `w-64` (256px)
- Button sizes reduced to fit

#### "Buttons are cut off or not visible"

**Solution**: Fixed with responsive sizing
- Play button: 64x64px (was 80x80px)
- Other buttons: `px-4 py-2` (was `px-6 py-3`)
- Control panel properly sized

#### "Animations not available"

**Solution**:
1. Check if `animations.json` exists in project folder
2. If missing, **regenerate the lecture** (animations added in v2.0)
3. Go to 🎬 Generate tab → Generate again

#### "Player loads but nothing plays"

**Solution**:
- Open browser console: `F12` → Console tab
- Look for errors
- Verify files exist:
  ```powershell
  Get-ChildItem ~\Lectures\{project}\narration.mp3
  Get-ChildItem ~\Lectures\{project}\animations.json
  Get-ChildItem ~\Lectures\{project}\slide_timings.json
  ```

#### "Only text fading in/out, no real animations"

**Cause**: AI-generated animations might be too simple

**Solutions**:
1. **Check animations.json content**:
   ```powershell
   Get-Content ~\Lectures\{project}\animations.json | ConvertFrom-Json
   ```
   Look for varied `action` types (slideIn, highlight, pulse, zoom)

2. **Improve slide content**:
   - More detailed bullet points
   - Clear structure
   - Better prompts help AI generate better animations

3. **Manually edit animations.json** (advanced):
   ```json
   {
     "slides": [
       {
         "slide_number": 1,
         "start_time": 0,
         "end_time": 10.5,
         "steps": [
           {
             "id": 1,
             "text": "Photosynthesis: Nature's Energy Factory",
             "action": "zoom",
             "duration": 2.0,
             "hint": "Watch how the title appears!",
             "element": "title"
           },
           {
             "id": 2,
             "text": "Plants convert sunlight into chemical energy",
             "action": "slideIn",
             "duration": 2.5,
             "hint": "This is the core process",
             "element": "bullet"
           }
         ]
       }
     ]
   }
   ```

### Backend Issues

#### "Cannot connect to Ollama"

**Solution**:
```powershell
# Check if Ollama is running
ollama serve

# Pull required models
ollama pull llama3.1:latest
ollama pull llama3.2:3b
```

#### "Slow generation times"

**Solution**:
- Close other applications
- Ensure GPU is being used (NVIDIA GPU required)
- Check Task Manager for GPU utilization
- Disable parallel processing if causing issues (edit `api.py`)

### Frontend Issues

#### "npm run tauri:dev fails"

**Solution**:
```powershell
# Reinstall dependencies
cd ui
Remove-Item node_modules -Recurse -Force
Remove-Item package-lock.json
npm install
npm run tauri:dev
```

#### "GSAP animations not working"

**Solution**:
```powershell
# Verify GSAP installation
cd ui
npm list gsap
# If not installed:
npm install gsap@3.13.0
```

---

## 🏗️ Architecture

### Tech Stack

- **Frontend**: 
  - Tauri (Rust) - Desktop framework
  - Vue 3 - Reactive UI components
  - Tailwind CSS - Styling
  - GSAP 3.13.0 - Professional animations

- **Backend**: 
  - Python FastAPI - API server
  - Ollama - Local LLM inference
  - Microsoft Edge TTS - Speech synthesis
  - FFmpeg - Video generation

- **AI Models**:
  - `llama3.1:latest` - Prosody tagging, content generation
  - `llama3.2:3b` - Quizzes, animations (smaller/faster)

### Data Flow

```
User Input (Topic/Document)
        ↓
Backend API (FastAPI)
        ↓
Content Generation (Ollama + LLM)
        ↓
Parallel Processing:
├── Slide Generation (PPTX)
├── Prosody Tagging (Ollama)
├── Speech Synthesis (Edge TTS)
├── Animation Steps (Ollama 3.2:3b)
└── Quiz Generation (Ollama 3.2:3b)
        ↓
Output Files:
├── presentation.pptx
├── narration.mp3
├── presentation_video.mp4
├── slide_timings.json
├── animations.json
└── quiz_data.json
        ↓
Frontend Display:
├── 📺 Viewer (video playback)
├── 🎭 Interactive (GSAP animations)
└── 🎓 Study Mode (quizzes)
```

### File Organization

```
LECTRA/
├── sidecar/               # Backend
│   ├── app/
│   │   ├── api.py         # Main FastAPI server
│   │   ├── services/
│   │   │   ├── ollama_client.py    # LLM calls
│   │   │   ├── edge_tts_client.py  # TTS
│   │   │   └── pptx_generator.py   # Slides
│   │   └── utils/
│   └── requirements.txt
│
├── ui/                    # Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── DocumentNotebook.vue     # Main UI
│   │   │   ├── LecturePlayer.vue        # Interactive player
│   │   │   └── InteractiveStudyMode.vue # Quiz system
│   │   └── main.js
│   ├── package.json       # Includes gsap@3.13.0
│   └── src-tauri/         # Rust backend
│
└── README.md              # This file
```

### API Endpoints

**Generation**:
- `POST /generate` - Generate lecture from topic
- `POST /generate_from_document` - Generate from uploaded file
- `POST /generate_slide_deck` - Create PPTX only

**Data Retrieval**:
- `GET /projects` - List all generated lectures
- `GET /get_slide_timings` - Get slide timing data
- `GET /get_animations` - Get animation steps
- `GET /quiz_data` - Get quiz questions

**Utilities**:
- `GET /voices` - List available TTS voices
- `GET /health` - Server health check

### Animation System Architecture

```
Slide Content → Ollama (llama3.2:3b) → Animation JSON
                        ↓
                {
                  "steps": [
                    {
                      "id": 1,
                      "text": "Content to reveal",
                      "action": "fadeIn",
                      "duration": 2.0,
                      "hint": "Helpful tip",
                      "element": "text"
                    }
                  ]
                }
                        ↓
                LecturePlayer.vue (Frontend)
                        ↓
                GSAP Animation Engine
                        ↓
                Rendered 60 FPS animations
```

---

## 📊 Performance Benchmarks

### RTX 5090 Optimized

| Task | Before | After | Speedup |
|------|--------|-------|---------|
| LLM Calls | 45-60s | 8-12s | 5-10x |
| Image Fetching | 20-30s | 5-7s | 3-5x |
| PPTX Creation | 30-40s | 15-20s | 2x |
| **Total** | **150-250s** | **50-70s** | **3-4x** |

### Optimization Techniques

1. **Parallel LLM Calls**: Process multiple slides simultaneously
2. **Async Image Downloads**: Fetch images concurrently
3. **Overlapped PPTX Creation**: Start building while images download
4. **GPU Acceleration**: Leverages RTX 5090 for LLM inference
5. **Caching**: Reuse processed content when possible

---

## 🎯 Best Practices

### For Learning (Interactive Mode)

1. Use **🎭 Interactive mode** while actively studying
2. Click **Next** after understanding each concept
3. Use **Replay** if confused or need to see again
4. Click **Hint** for AI-generated explanations
5. Adjust **Speed** based on difficulty (0.5x for complex topics)

### For Sharing (Video Mode)

1. Use **📺 Viewer mode** to watch the rendered video
2. Share the `.mp4` file via email/cloud storage
3. Recipients don't need LECTRA to view
4. Good for offline viewing

### For Presenting

1. Use **🎭 Interactive mode** in Fullscreen
2. Control pace based on audience questions
3. Replay sections as needed
4. Show hints when asked

### Content Creation Tips

1. **Clear Structure**: Well-organized content → better animations
2. **Concise Bullets**: Short points are easier to animate
3. **Good Titles**: Descriptive titles help AI generate better steps
4. **Speaker Notes**: Detailed notes → more context for animations

---

## 🔐 Requirements

### System Requirements

- **OS**: Windows 10/11 (with PowerShell)
- **GPU**: NVIDIA RTX 3000+ series (recommended: RTX 5090)
- **RAM**: 16GB minimum, 32GB recommended
- **Storage**: 10GB for models and dependencies

### Software Dependencies

- **Python**: 3.10+
- **Node.js**: 16+
- **Rust**: Latest stable (for Tauri)
- **Ollama**: Latest version
- **FFmpeg**: Installed and in PATH

---

## 📝 Version History

### v2.0 (Current)
- ✨ Added interactive animations with GSAP
- 🎭 New Interactive Player tab
- 🎓 Fixed quiz checkpoint timing
- 🌐 Language-aware quiz generation (Hindi support)
- 📺 Enhanced viewer with speed control, share, download
- 🐛 Fixed slide timing accuracy
- 📚 Container overflow fixes
- 🎨 Responsive button sizing

### v1.x
- Initial release
- Basic video generation
- Quiz system
- Document processing
- Performance optimizations

---

## 🤝 Contributing

Found a bug? Have a suggestion?

1. Check existing issues
2. Create detailed bug report with:
   - Steps to reproduce
   - Expected vs actual behavior
   - Console errors (if any)
   - System info

---

## 📄 License

[Your license here]

---

## 🎉 Quick Reference Card

| I want to... | Go to... |
|--------------|----------|
| Generate a new lecture | 📚 Document Notebook → 🎬 Generate |
| See interactive animations | 🎭 Interactive tab |
| Watch the video | 📺 Viewer tab |
| Take quizzes | 🎓 Study Mode tab |
| Share a lecture | 📺 Viewer → Share button |
| Adjust playback speed | Interactive or Viewer → Speed dropdown |
| View hints | 🎭 Interactive → 💡 Hint button |

---

**Need help?** Check the [Troubleshooting](#-troubleshooting) section above!
