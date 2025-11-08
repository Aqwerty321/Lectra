# LECTRA �

**Lecture Creation & Training with Realistic Audio** — AI-powered desktop application for generating educational content with natural speech, interactive quizzes, and multimedia presentations.

---

## 🌟 Features

### Core Functionality
- 🎙️ **Natural AI Speech**: Microsoft Edge TTS with AI-powered prosody tagging
- 📊 **Auto-Generated Presentations**: Create PowerPoint slides from documents or topics
- 🎬 **Video Generation**: Synchronized video lectures with narration
- � **Document Processing**: Support for PDF, DOCX, PPTX, and plain text
- 🌍 **Multilingual**: English and Hindi with multiple voice options

### Interactive Study Mode (NEW!)
- 🎓 **AI-Generated Quizzes**: Automatic MCQ generation using Ollama LLM
- ⏸️ **Smart Video Pausing**: Quiz checkpoints at configurable intervals
- 💡 **Hints & Explanations**: Detailed feedback for every question
- 📈 **Progress Tracking**: Real-time scores, accuracy, and session analytics
- 🎨 **Beautiful Glassmorphism UI**: Wood texture with frosted glass design

### Performance
- ⚡ **RTX 5090 Optimized**: Sub-60-second presentation generation
- 🚀 **5-10x faster** LLM calls via parallel execution
- 🖼️ **3-5x faster** image fetching with async downloads
- 📦 **2x faster** PPTX creation with overlapped processing
- ⏱️ **3-4x overall speedup** (150-250s → 50-70s)

---

## 🏗️ Architecture

- **Frontend**: Tauri (Rust) + Vue 3 + Tailwind CSS
- **Backend**: Python FastAPI server
- **AI Models**: 
  - Ollama (llama3.1:latest for prosody, llama3.2:3b for quizzes)
  - Microsoft Edge TTS for speech synthesis
- **Database**: PostgreSQL (optional) for job logging
- **Video**: FFmpeg for video generation

---

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

#### Windows
```powershell
# Run setup script
.\setup-v2.ps1

# Launch application
.\launch.ps1
```

#### Linux/macOS
```bash
# Make script executable and run
chmod +x setup.sh
./setup.sh

# Launch application
./launch.sh
```

### Option 2: Manual Setup

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

---

## 📋 Prerequisites

### Required Software
- **Python 3.11+** - Backend server
- **Node.js 18+** - Frontend build
- **Rust** - Tauri framework
- **FFmpeg** - Video processing
- **Ollama** - AI model runtime

### Recommended
- **8GB+ RAM** (16GB for quiz generation)
- **GPU** for faster AI processing
- **SSD** for better performance

---

## 🎯 Usage

### Creating a Lecture

1. **Upload Document** or **Generate from Topic**
   - Upload PDF, DOCX, PPTX, or enter a topic
   - Select language and voice
   - Choose whether to generate video

2. **Processing**
   - Document is analyzed and slides are created
   - AI adds natural prosody to narration
   - Audio is synthesized with Edge TTS
   - (Optional) Video is generated with slides + audio

3. **Output**
   - PowerPoint presentation with notes
   - Audio narration (MP3)
   - Video lecture (MP4)
   - Slide timings and subtitles (VTT)

### Interactive Study Mode

1. **Select Project** with existing video
2. **Configure Settings**
   - Quiz frequency (every 2-5 slides)
   - Difficulty level (easy/medium/hard)
3. **Study Session**
   - Video plays automatically
   - Pauses at checkpoints for quizzes
   - 5 AI-generated MCQs per checkpoint
   - Real-time scoring and feedback
   - Hints available without penalty

---

## 📁 Project Structure

```
LECTRA/
├── sidecar/               # Python backend
│   ├── app/
│   │   ├── api.py        # FastAPI routes
│   │   ├── config.py     # Configuration
│   │   └── services/
│   │       ├── quiz_generator.py  # AI quiz generation
│   │       └── ...
│   └── requirements.txt
├── ui/                    # Tauri + Vue frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── DocumentNotebook.vue
│   │   │   └── InteractiveStudyMode.vue
│   │   └── App.vue
│   └── src-tauri/        # Rust/Tauri code
├── .env.example          # Environment template
├── setup-v2.ps1          # Windows setup
├── setup.sh              # Linux/Mac setup
├── launch.ps1            # Windows launcher
└── DEPLOYMENT.md         # Deployment guide
```

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Ollama API for AI
OLLAMA_URL=http://127.0.0.1:11434

# Output directory for generated content
OUTPUT_ROOT=~/Lectures

# FFmpeg binary path
FFMPEG_BIN=/usr/bin/ffmpeg

# Default TTS voices
DEFAULT_EN_VOICE=en-US-GuyNeural
DEFAULT_HI_VOICE=hi-IN-SwaraNeural

# Database (optional)
DATABASE_URL=postgres://user:pass@localhost:5432/lectra
```

---

## 📖 Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide
- **[STUDY_MODE_GUIDE.md](STUDY_MODE_GUIDE.md)** - Interactive study mode features
- **[OPTIMIZATION_README.md](OPTIMIZATION_README.md)** - Performance optimizations
- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture details

---

## 🐛 Troubleshooting

### Common Issues

**Port 8765 already in use**
```powershell
# Windows
Get-Process -Name python | Stop-Process -Force

# Linux/Mac
lsof -i :8765 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

**Ollama connection failed**
```bash
# Check Ollama is running
ollama list

# Pull required models
ollama pull llama3.1:latest
ollama pull llama3.2:3b
```

**Video player not working**
- Ensure FFmpeg is installed and in PATH
- Check file permissions for Lectures folder
- Verify convertFileSrc is used in Tauri

**Quiz generation fails**
- Ensure Ollama is running with llama3.2:3b
- Check sufficient RAM (3GB+ needed)
- Verify metadata.json exists for project

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📜 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Microsoft Edge TTS** - High-quality speech synthesis
- **Ollama** - Local LLM runtime
- **Tauri** - Lightweight desktop framework
- **FastAPI** - Modern Python web framework
- **Vue 3** - Progressive JavaScript framework

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/lectra/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/lectra/discussions)
- **Documentation**: See docs folder

---

**Made with ❤️ for educators and learners**

# 2. Configure environment
cp .env.example .env
# Edit .env with your settings

# 3. Build Python sidecar
cd sidecar
pip install -r requirements.txt
cd ..
.\scripts\build_sidecar.ps1

# 4. Install UI dependencies
cd ui
npm install
cd ..

# 5. Run in dev mode
cd ui
npm ru

### Production Build

```powershell
cd ui
npm run tauri build
# Installer will be in ui/src-tauri/target/release/bundle/
```

## Project Structure

```
LECTRA/
├── ui/                    # Vue 3 + Tailwind frontend
│   ├── src/
│   │   ├── components/    # NavBar, HeroLogo, GeneratorPanel, etc.
│   │   ├── assets/images/ # Wood textures, logo
│   │   └── App.vue
│   └── package.json
├── sidecar/               # Python FastAPI backend
│   ├── app/
│   │   ├── services/      # ollama_client, tts_engine, timing, etc.
│   │   ├── api.py         # FastAPI routes
│   │   └── config.py
│   └── requirements.txt
├── scripts/
│   └── build_sidecar.ps1  # PyInstaller bundler
└── bin/
    └── lecture-sidecar.exe # Generated sidecar binary
```

## Usage

1. **Launch App**: Double-click LECTRA icon
2. **Select Language**: EN or HI
3. **Input Text**: Type or use "big sample"
4. **Configure Voice**: Choose from presets or enter custom EdgeTTS voice
5. **Generate**: Creates `~/Lectures/<project>/` with:
   - `tagged.txt` — Text with prosody tags
   - `ssml.xml` — Azure SSML markup
   - `audio.mp3` — Generated speech
   - `timings.json` — Per-sentence timing data
   - `subs.vtt` — WebVTT subtitles
   - **NEW**: `presentation.pptx` — AI-generated slides with images
   - **NEW**: `presentation_video.mp4` — Synced video with audio

## ⚡ Performance Optimizations

### Parallel Processing
- **LLM Calls**: All slides generated in parallel with `asyncio.gather()` (5-10x faster)
- **Image Fetching**: All images downloaded concurrently (3-5x faster)
- **PPTX Creation**: Overlapped with image fetching (2x faster)
- **Connection Pooling**: Shared HTTP sessions reduce overhead

### Real-time Profiling
Every generation shows timing breakdown:
```
[⏱] Step 1: Generate Outline: 8.42s
[⏱] Step 2: Generate Script (Parallel): 12.35s
[⏱] Step 3+4: Images + PPTX (Parallel): 15.67s
[⏱] Step 8: Synthesize Audio (EdgeTTS): 18.45s
------------------------------------------------------------
TOTAL: 69.69s
```

### Performance Documentation
- **[OPTIMIZATION_README.md](OPTIMIZATION_README.md)** — Quick start guide
- **[PERFORMANCE_OPTIMIZATION.md](PERFORMANCE_OPTIMIZATION.md)** — Comprehensive 2000+ line guide
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** — One-page reference card

## API Endpoints (Sidecar)

- `GET /healthz` — Health check
- `POST /generate` — Full pipeline (tagging → SSML → audio → timing)
- `POST /estimate` — Timing only (no audio generation)
- `POST /generate_presentation` — **NEW**: Complete presentation generation (outline → slides → PPTX → audio → video)

## Timing Formula

```
words = tokenize(sentence_without_tags)
base_wpm = {en: 165, hi: 150, voice_overrides}
rate_pct = last [rate=±##%] in sentence or fallback
eff_wpm = clamp(base_wpm * (1 + rate_pct/100), 80, 240)
spoken_sec = (words / eff_wpm) * 60
punct_ms = count(",")*200 + count(".")*450 + count("…")*700
tag_pauses = sum([pause=###ms])
duration_sec = spoken_sec + (punct_ms + tag_pauses)/1000
```

## Tech Stack

- Python, FastAPI, EdgeTTS, FFmpeg
- Ollama, Llama-3.1
- PostgreSQL
- Vue 3, Tailwind CSS, Tauri
- Rust (sidecar management)

## Made with ❤️ by Team Just-Git-Gud

---

**License**: MIT  
**Repo**: [github.com/your-org/lectra](https://github.com/your-org/lectra)
