# 🎓 LECTRA v2.0 - Complete Feature Overview

## 🌟 What's New

### 1. Document Upload System
**Upload & Process PDF/DOCX Documents**
- Drag-and-drop interface for PDF and DOCX files
- Automatic text extraction with page/paragraph preservation
- Intelligent chunking (1000 chars with 200 char overlap)
- Topic detection using heuristics
- Real-time processing feedback

**Technical Details:**
- `PyPDF2` for PDF parsing
- `python-docx` for DOCX parsing
- Sentence-boundary-aware chunking
- Metadata persistence (JSON)

### 2. Vector Database Integration
**ChromaDB + Ollama Embeddings**
- Persistent vector storage per project
- `nomic-embed-text` embeddings (768-dim)
- Fast semantic search (<100ms)
- Collection management (list, create, delete)

**Technical Details:**
- ChromaDB with SQLite backend
- Ollama API integration (http://localhost:11434)
- Batch embedding generation (10 chunks at a time)
- Metadata tracking (chunk_id, position, length)

### 3. RAG-Powered Presentation Generation
**Context-Aware Content Creation**
- Query-based chunk retrieval (top 10 relevant)
- Relevance scoring (cosine similarity)
- Context injection into LLM prompts
- Automatic slide generation from retrieved content

**Workflow:**
```
User Query → Embedding → Vector Search → Top 10 Chunks
    ↓
Combine Context (10,000 char limit) → LLM Outline Generation
    ↓
Slide Content + Images → PPTX Creation → TTS Synthesis
    ↓
Video Generation with Subtitles
```

### 4. Subtitle Embedding
**Hardcoded Subtitles in Every Video**
- SRT generation from sentence timings
- FFmpeg subtitle filter for burn-in
- Professional styling (white text, black outline, shadow)
- Sentence-level synchronization

**Subtitle Specs:**
- Font: Arial, 24pt
- Position: Bottom (30px margin from edge)
- Colors: White text (#FFFFFF), black outline (#000000)
- Border: 2px outline + 1px shadow
- Format: SRT (SubRip)

### 5. Integrated Video Player
**Watch Presentations In-App**
- Native HTML5 video player
- Project-based video library
- Direct file:// protocol loading
- Full controls (play, pause, seek, volume, fullscreen)

**Features:**
- Auto-load video on project selection
- File size display
- Path information
- Responsive sizing (max 600px height)

### 6. Notebook Interface
**4-Tab Organization**

#### 📤 Upload Tab
- Project name input
- File selector (PDF/DOCX only)
- Upload progress indicator
- Processing result display
- Topic preview (first 10)

#### 📖 Library Tab
- Grid view of all projects
- Status indicators (video ✅, presentation ✅, docs 📚)
- Click-to-select functionality
- Auto-refresh on upload

#### 🎬 Generate Tab
- Collection selector (dropdown)
- Topic/query input
- Language & voice selection
- Video generation toggle
- Progress feedback
- Result display with RAG metrics

#### 📺 Viewer Tab
- Project selector
- Video player with native controls
- File path display
- Empty state messaging

### 7. Enhanced Timing System
**Robust Audio Sync**
- FFprobe for actual audio duration
- Scale factor calculation (actual/estimated)
- Title slide handling (fixed 4s duration)
- Sentence-to-slide mapping improvements
- Coverage validation (95-105% target)

**Technical Improvements:**
- Fallback to pydub if FFmpeg unavailable
- Common Windows FFmpeg paths checked
- Error handling with graceful degradation

### 8. Theme Consistency
**Warm Wood Aesthetic**
- Dark wood navbar (#3a2618)
- Light wood cards (#d4a574)
- Amber accents (#f59e0b)
- Orange highlights (#ea580c)
- Smooth transitions and animations

**UI Polish:**
- Fade-in animations
- Hover effects
- Loading spinners
- Status toast notifications
- Emoji icons throughout

## 📊 Performance Metrics

| Operation | Duration | Notes |
|-----------|----------|-------|
| PDF upload (1MB) | 2-5s | Depends on page count |
| Text chunking | <1s | For 100k characters |
| Embedding generation | 0.5s | Per chunk via Ollama |
| Vector search | <100ms | For 1000 chunks |
| Presentation gen | 30-60s | Full pipeline |
| Video encoding | 10s/min | With subtitles |

## 🔧 Architecture Overview

### Backend Services

#### `document_processor.py`
- `extract_text_from_pdf()` - PyPDF2 extraction
- `extract_text_from_docx()` - python-docx extraction
- `chunk_text()` - Intelligent chunking with overlap
- `extract_topics_from_text()` - Header detection
- `process_document()` - Full pipeline orchestration

#### `vector_store.py`
- `VectorStore` class - ChromaDB wrapper
- `get_embedding()` - Ollama API calls
- `create_collection()` - Collection management
- `add_documents()` - Batch embedding + storage
- `search_similar()` - Semantic search
- `get_collection_stats()` - Metadata queries

#### `sync_calculator.py` (Enhanced)
- `probe_media_duration()` - FFprobe/pydub
- `calculate_slide_timings_from_audio()` - Timing sync
- Title slide support with fixed durations
- Fallback chain (FFprobe → FFmpeg → pydub)

#### `video_generator.py` (Enhanced)
- `generate_srt_subtitles()` - SRT file creation
- `create_video_from_slides()` - FFmpeg with subtitle filter
- Subtitle burning with custom styling
- Sentence timing integration

### Frontend Components

#### `DocumentNotebook.vue` (NEW)
- 4-tab interface (Upload, Library, Generate, Viewer)
- File upload with drag-and-drop
- Project management
- Video player integration
- Real-time status updates

#### `App.vue` (Enhanced)
- New #notebook section
- DocumentNotebook component integration
- Scroll-to-section navigation

#### `NavBar.vue` (Enhanced)
- New "📚 Notebook" nav item
- Emoji icons for all sections

### API Endpoints (NEW)

```
POST /upload_document
  - Multipart file upload
  - Document processing pipeline
  - Vector storage
  - Returns: topics, chunk count, collection name

POST /generate_from_topic
  - RAG-powered generation
  - Vector search + context injection
  - Full presentation pipeline
  - Returns: slides, audio, video paths + RAG metrics

GET /list_collections?project={name}
  - List ChromaDB collections
  - Collection statistics
  - Returns: array of collection objects

GET /get_video?project={name}
  - Get video file path
  - File existence check
  - Returns: path, size, exists flag

GET /list_projects
  - List all ~/Lectures projects
  - Status indicators (video, pptx, docs)
  - Returns: array of project objects
```

## 🎯 Use Cases

### 1. Academic Lectures
**Upload:** Course textbook PDF
**Query:** "Chapter 5: Neural Networks"
**Result:** Presentation covering NN basics with relevant diagrams

### 2. Training Materials
**Upload:** Company policy DOCX
**Query:** "Remote work guidelines"
**Result:** Narrated slides on work-from-home policies

### 3. Research Presentations
**Upload:** Research paper PDF
**Query:** "Methodology section"
**Result:** Technical slides explaining research methods

### 4. Study Notes
**Upload:** Semester notes PDF
**Query:** "Final exam topics"
**Result:** Review presentation covering key concepts

## 🚀 Getting Started

### Quick Start (5 minutes)

1. **Run Setup**
   ```powershell
   .\setup-v2.ps1
   ```

2. **Start LECTRA**
   ```powershell
   .\launch.ps1
   ```

3. **Navigate to Notebook**
   - Click "📚 Notebook" in navbar

4. **Upload Document**
   - Enter project name: "test-lecture"
   - Select a PDF/DOCX file
   - Click "🚀 Upload & Process"
   - Wait for processing (shows topics)

5. **Generate Presentation**
   - Go to "🎬 Generate" tab
   - Select your collection
   - Enter topic: "Introduction"
   - Click "✨ Generate Presentation"
   - Wait 30-60 seconds

6. **Watch Video**
   - Go to "📺 Viewer" tab
   - Select "test-lecture"
   - Video plays with subtitles!

## 💡 Pro Tips

1. **Better Topic Extraction**: Use descriptive section headers in your documents
2. **Optimal Queries**: Be specific - "supervised learning algorithms" > "AI"
3. **Chunk Size**: Default 1000 chars is ideal for most documents
4. **Collection Names**: Automatically generated as `{project}_{filename}`
5. **Context Limits**: System uses first 10,000 chars of retrieved content
6. **Voice Selection**: Experiment with different voices for variety
7. **Video Quality**: Higher DPI = larger files but better quality
8. **Subtitle Readability**: Works best with dark or busy backgrounds

## 🐛 Common Issues & Solutions

### "Ollama connection refused"
**Problem:** Ollama server not running
**Solution:** `ollama serve` in terminal

### "ChromaDB collection not found"
**Problem:** No documents uploaded yet
**Solution:** Go to Upload tab, process a document first

### "FFmpeg not found"
**Problem:** FFmpeg not in PATH or C:\ffmpeg\bin
**Solution:** Install FFmpeg, place in C:\ffmpeg, or add to PATH

### Video doesn't load
**Problem:** Browser security restrictions on file:// URLs
**Solution:** Use Tauri app (not web browser) or copy path to native player

### Embeddings taking too long
**Problem:** Large document with many chunks
**Solution:** Be patient - first upload is slower, subsequent searches are fast

### No topics detected
**Problem:** Document has no clear headers
**Solution:** Manually enter topic queries in Generate tab

## 🔮 Roadmap

### v2.1 (Next Release)
- [ ] Citation tracking (chunk → slide mapping)
- [ ] Multi-document search
- [ ] Custom embedding models
- [ ] Separate SRT export
- [ ] Configurable subtitle styling

### v2.2
- [ ] OCR for scanned PDFs
- [ ] Batch document upload
- [ ] Document preprocessing pipeline
- [ ] Chapter markers in video
- [ ] Interactive timeline

### v3.0
- [ ] Voice cloning integration
- [ ] Real-time collaboration
- [ ] Cloud storage sync
- [ ] Mobile app
- [ ] Presentation templates

## 📄 Credits

**Built with:**
- FastAPI - Backend API
- Vue 3 + Vite - Frontend
- Tauri - Desktop app framework
- ChromaDB - Vector database
- Ollama - Local LLM & embeddings
- FFmpeg - Video processing
- EdgeTTS - Text-to-speech
- PyPDF2 - PDF parsing
- python-docx - DOCX parsing

**AI Models:**
- `llama3.1` - Content generation
- `nomic-embed-text` - Document embeddings

---

**Made with ❤️ by the LECTRA team**

*Turn any document into an engaging video lecture!*
