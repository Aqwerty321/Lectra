# LECTRA Deployment Guide

## Prerequisites

### Required Software
1. **Python 3.11+** - Backend server
2. **Node.js 18+** - Frontend build system
3. **Rust** - Tauri desktop app framework
4. **FFmpeg** - Video processing
5. **Ollama** - AI model runtime (for quiz generation)

### System Requirements
- **OS**: Windows 10/11, macOS 10.15+, or Linux
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 2GB for installation + space for generated content
- **GPU**: Optional, improves AI performance

---

## Quick Start (Development)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/lectra.git
cd lectra
```

### 2. Setup Backend (Python)
```bash
cd sidecar

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Or (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp ../.env.example ../.env
# Edit .env with your settings
```

### 3. Setup Frontend (Tauri + Vue)
```bash
cd ui

# Install Node dependencies
npm install

# Build Tauri app (development)
npm run tauri dev
```

### 4. Start Backend Server
```bash
cd sidecar
# With virtual environment activated
python -m uvicorn app.api:app --host 127.0.0.1 --port 8765
```

### 5. Install Ollama (For AI Quiz Generation)
- Download from: https://ollama.ai
- Install the llama3.2:3b model:
```bash
ollama pull llama3.2:3b
```

---

## Production Deployment

### Option 1: Desktop Application (Recommended)

#### Build Standalone App
```bash
cd ui
npm run tauri build
```

This creates:
- **Windows**: `ui/src-tauri/target/release/lectra.exe`
- **macOS**: `ui/src-tauri/target/release/bundle/macos/LECTRA.app`
- **Linux**: `ui/src-tauri/target/release/lectra`

#### Distribution
1. Package the executable with:
   - `sidecar/` folder (Python backend)
   - `.env` file (configuration)
   - `requirements.txt`
   - FFmpeg binaries

2. Create installer with:
   - [Inno Setup](https://jrsoftware.org/isinfo.php) (Windows)
   - [create-dmg](https://github.com/create-dmg/create-dmg) (macOS)
   - [AppImage](https://appimage.org/) (Linux)

### Option 2: Server Deployment

#### Backend API Server
```bash
# Install system dependencies
sudo apt install python3-pip ffmpeg

# Setup Python environment
cd sidecar
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with production server
pip install gunicorn
gunicorn app.api:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8765
```

#### Frontend Web App
```bash
cd ui
npm run build

# Serve static files with nginx/caddy
# Point to ui/dist folder
```

---

## Configuration

### Environment Variables (.env)

```bash
# Ollama API for AI quiz generation
OLLAMA_URL=http://127.0.0.1:11434

# PostgreSQL database (optional)
DATABASE_URL=postgres://user:pass@localhost:5432/lectra

# Output folder for generated content
OUTPUT_ROOT=~/Lectures

# FFmpeg binary path
FFMPEG_BIN=/usr/bin/ffmpeg  # Linux/Mac
# FFMPEG_BIN=C:\ffmpeg\bin\ffmpeg.exe  # Windows

# Default TTS voices
DEFAULT_EN_VOICE=en-US-GuyNeural
DEFAULT_HI_VOICE=hi-IN-SwaraNeural
```

### Tauri Configuration (ui/src-tauri/tauri.conf.json)

Key settings:
- `allowlist.protocol.assetScope`: File access permissions
- `build.distDir`: Frontend build output
- `build.beforeDevCommand`: Dev server command
- `build.beforeBuildCommand`: Production build command

---

## Docker Deployment (Optional)

### Backend Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y ffmpeg

# Install Python dependencies
COPY sidecar/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY sidecar/ .

# Expose port
EXPOSE 8765

# Run server
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8765"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8765:8765"
    volumes:
      - ./Lectures:/app/Lectures
    environment:
      - OLLAMA_URL=http://ollama:11434
      - OUTPUT_ROOT=/app/Lectures

  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama:/root/.ollama

volumes:
  ollama:
```

---

## Post-Deployment Checklist

### Security
- [ ] Change default API keys/secrets
- [ ] Enable HTTPS for production
- [ ] Configure CORS appropriately
- [ ] Set up firewall rules
- [ ] Enable rate limiting

### Performance
- [ ] Configure FFmpeg hardware acceleration
- [ ] Set up Ollama GPU support
- [ ] Enable frontend caching
- [ ] Optimize database queries
- [ ] Monitor resource usage

### Monitoring
- [ ] Set up logging (Winston/Pino)
- [ ] Configure error tracking (Sentry)
- [ ] Add health check endpoints
- [ ] Set up uptime monitoring
- [ ] Track user analytics

### Backup
- [ ] Backup generated content regularly
- [ ] Export user data/settings
- [ ] Version control configuration
- [ ] Document disaster recovery plan

---

## Troubleshooting

### Common Issues

#### "Port 8765 already in use"
```bash
# Windows
netstat -ano | findstr :8765
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8765
kill -9 <PID>
```

#### "FFmpeg not found"
- Ensure FFmpeg is installed: `ffmpeg -version`
- Update FFMPEG_BIN path in .env

#### "Ollama connection failed"
- Check Ollama is running: `ollama list`
- Verify OLLAMA_URL in .env
- Pull required model: `ollama pull llama3.2:3b`

#### "Video player blank/not loading"
- Check file permissions for Lectures folder
- Verify convertFileSrc is used in frontend
- Check protocol allowlist in tauri.conf.json

#### "Quiz generation fails"
- Ensure metadata.json exists for project
- Check Ollama model is loaded
- Verify sufficient RAM (3GB+ for llama3.2:3b)

---

## Maintenance

### Updates
```bash
# Update Python dependencies
cd sidecar
pip install --upgrade -r requirements.txt

# Update Node dependencies
cd ui
npm update

# Update Ollama models
ollama pull llama3.2:3b
```

### Database Migrations
```bash
cd sidecar
alembic upgrade head
```

### Logs
- Backend logs: `sidecar/logs/`
- Frontend logs: Browser DevTools Console
- Tauri logs: `~/.local/share/lectra/logs/` (Linux)

---

## Support

- **Documentation**: See [README.md](README.md)
- **Issues**: https://github.com/yourusername/lectra/issues
- **Discussions**: https://github.com/yourusername/lectra/discussions
- **Email**: support@lectra.app

---

## License

MIT License - See [LICENSE](LICENSE) file for details
