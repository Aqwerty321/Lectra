# 🎓 LECTRA v2.0 - Document Notebook System

## 🚀 New Features

### 📚 Document-Based Learning
- **Upload PDF/DOCX files** for automatic processing
- **Intelligent chunking** with overlap for better context
- **Vector embeddings** using Ollama's `nomic-embed-text`
- **ChromaDB storage** for persistent vector search

### 🧠 RAG-Powered Generation
- **Semantic search** through uploaded documents
- **Topic-based extraction** - query specific subjects
- **Context-aware slides** - generates presentations from relevant chunks
- **Relevance scoring** - see which parts of the document were used

### 📺 Integrated Video Player
- **In-app video viewer** - watch generated presentations immediately
- **Project library** - browse all your generated content
- **Subtitle support** - hardcoded subtitles in all videos

### 🎨 Enhanced UI
- **Notebook interface** with 4 tabs:
  - 📤 **Upload**: Process new documents
  - 📖 **Library**: Browse existing projects
  - 🎬 **Generate**: Create presentations from topics
  - 📺 **Viewer**: Watch generated videos
- **Consistent theme** with warm wood tones and amber accents
- **Real-time progress** indicators

## 🛠️ Installation

### 1. Install New Dependencies

```bash
cd sidecar
pip install -r requirements.txt
```

New packages:
- `PyPDF2` - PDF text extraction
- `python-docx` - DOCX parsing
- `chromadb` - Vector database

### 2. Install Ollama Embedding Model

```bash
ollama pull nomic-embed-text
```

This ~274MB model generates embeddings for semantic search.

### 3. Ensure FFmpeg is Available

For video generation and subtitles:
- **Windows**: Place FFmpeg in `C:\ffmpeg\bin\`
- **Linux/Mac**: Install via package manager

## 📖 Usage Guide

### Workflow 1: Upload & Generate from Document

1. **Upload Document**
   - Go to Notebook tab
   - Click "Upload"
   - Select project name (e.g., "ml-course")
   - Choose PDF/DOCX file
   - Click "Upload & Process"
   - System extracts text, chunks it, generates embeddings, stores in ChromaDB

2. **Generate Presentation**
   - Switch to "Generate" tab
   - Select your collection
   - Enter a topic/query (e.g., "supervised learning")
   - Choose language & voice
   - Click "Generate Presentation"
   - System:
     - Searches vector DB for relevant chunks
     - Generates outline from retrieved context
     - Creates slides with images
     - Synthesizes narration with prosody
     - Builds video with subtitles

3. **Watch Video**
   - Switch to "Viewer" tab
   - Select your project
   - Video plays in-app with native controls

### Workflow 2: Browse Library

1. Go to "Library" tab
2. See all your projects with:
   - ✅ Video availability status
   - ✅ Presentation availability
   - 📚 Number of indexed documents
3. Click a project to jump to generation

## 🔧 Technical Architecture

### Document Processing Pipeline
```
PDF/DOCX → Text Extraction → Chunking (1000 chars, 200 overlap)
   ↓
Ollama nomic-embed-text → 768-dim vectors
   ↓
ChromaDB → Persistent storage with metadata
```

### RAG Generation Pipeline
```
User Query → Embedding → Vector Search (top 10)
   ↓
Retrieved Chunks → LLM Context → Outline Generation
   ↓
Slide Content → Image Search → PPTX Creation
   ↓
TTS Synthesis → Audio Chunks → MP3 Assembly
   ↓
FFmpeg → Video + Subtitles (burned-in)
```

### Video Generation Enhancements
- **Subtitle generation**: SRT format with sentence-level timing
- **FFmpeg burn-in**: Hardcoded white subtitles with black outline
- **Sync calculator**: FFprobe for actual duration vs estimates
- **Scale factor**: Corrects timing drift
- **Title slide handling**: Fixed 4s duration (no narration)

## 📂 Project Structure

```
~/Lectures/
  my-lecture/
    chroma_db/              # Vector database
      chroma.sqlite3
    document_metadata.json  # Upload info
    presentation.pptx       # Generated slides
    narration.mp3          # Full audio
    presentation_video.mp4 # Final video with subs
    slide_timings.json     # Timing data
    subtitles.srt          # Subtitle file
```

## 🎯 Advanced Features

### Chunk Overlap Strategy
- 1000 character chunks with 200 char overlap
- Breaks at sentence boundaries when possible
- Preserves context across chunk borders

### Embedding Model
- `nomic-embed-text` optimized for long-form text
- 768-dimensional vectors
- Trained on diverse datasets
- Excellent for educational content

### Subtitle Styling
```
Font: Arial, 24pt
Colors: White text, black outline/shadow
Position: Bottom (30px margin)
BorderStyle: 3 (outline + shadow)
```

### Timing Sync
- **Estimated timings**: From text analysis
- **Actual duration**: FFprobe of audio file
- **Scale factor**: actual / estimated
- **Coverage validation**: Warns if <95% or >105%

## 🐛 Troubleshooting

### "FFmpeg not found"
- **Fix**: Install FFmpeg or place in `C:\ffmpeg\bin\`
- **Fallback**: System uses pydub for audio duration

### "ChromaDB collection not found"
- **Fix**: Upload a document first
- **Check**: Go to Library tab to see collections

### "Ollama connection refused"
- **Fix**: Start Ollama: `ollama serve`
- **Verify**: `ollama list` should show `nomic-embed-text`

### Video won't play in browser
- **Fix**: Use native video player or VLC
- **Path**: Check `/get_video` endpoint for file location

### Upload fails with "Unsupported file type"
- **Fix**: Only PDF and DOCX are supported
- **Convert**: Use online tools to convert other formats

## 🔮 Future Enhancements

- [ ] Multi-document search across collections
- [ ] Citation tracking (which chunk → which slide)
- [ ] Interactive timeline in video player
- [ ] Export subtitles as separate SRT file
- [ ] Custom subtitle styling options
- [ ] Batch document upload
- [ ] Document preprocessing (OCR for scanned PDFs)
- [ ] Chapter markers in video
- [ ] Presentation templates
- [ ] Voice cloning integration

## 📊 Performance Notes

- **Document upload**: ~2-5 seconds per MB
- **Embedding generation**: ~0.5 seconds per chunk
- **Vector search**: <100ms for 1000 chunks
- **Presentation generation**: 30-60 seconds (depending on length)
- **Video encoding**: ~10 seconds per minute of content

## 🎨 Theme Colors

- **Dark Wood**: `#3a2618` (navbar, backgrounds)
- **Light Wood**: `#d4a574` (cards, sections)
- **Amber**: `#f59e0b` (accents, buttons)
- **Orange**: `#ea580c` (gradients, highlights)

## 💡 Tips & Tricks

1. **Topic queries**: Be specific for better chunk retrieval
2. **Document naming**: Use descriptive names for easy browsing
3. **Project organization**: One document per project recommended
4. **Voice selection**: Experiment with different voices for variety
5. **Context length**: System uses top 10,000 characters of retrieved content

## 📄 License

Same as LECTRA main license.

---

**Built with ❤️ using FastAPI, Vue 3, Tauri, ChromaDB, Ollama, and FFmpeg**
