# Changelog

All notable changes to LECTRA will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Interactive Study Mode with AI-generated quizzes
- Glassmorphism UI with wood texture theme
- Video viewer tab alongside study mode
- Automatic metadata.json generation from script.json
- Quiz generation with Ollama llama3.2:3b
- Real-time progress tracking in study sessions
- Hint system without score penalties
- Detailed answer explanations
- Multiple difficulty levels (easy/medium/hard)
- Configurable quiz frequency (2-5 slides)
- Video pause/resume at quiz checkpoints
- Session analytics (score, accuracy, duration)

### Changed
- Updated frontend to use glassmorphism design
- Made video paths OS-independent
- Improved quiz checkpoint calculation
- Enhanced error handling for quiz generation

### Fixed
- Video continues playing during quiz (now properly pauses)
- Hardcoded user paths removed for cross-platform compatibility
- Port 8765 conflict resolution
- Ollama connection error handling

---

## [2.0.0] - 2024-11-08

### Added
- Performance optimizations for RTX 5090
- Parallel LLM processing (5-10x faster)
- Async image downloading (3-5x faster)
- Overlapped PPTX creation (2x faster)
- Overall 3-4x speedup (150-250s → 50-70s)
- Comprehensive optimization documentation
- Benchmark suite for performance testing

### Changed
- Refactored generation pipeline for parallelism
- Optimized image fetching with connection pooling
- Improved PPTX creation with batch processing

### Fixed
- Memory leaks in long-running sessions
- Race conditions in parallel processing
- Image download timeout issues

---

## [1.5.0] - 2024-10-15

### Added
- Video generation with FFmpeg
- Slide timing synchronization
- Subtitle generation (VTT format)
- Multiple voice selection per language
- Document upload interface
- Library view for existing projects

### Changed
- Improved TTS quality settings
- Enhanced audio timing accuracy
- Better error messages

### Fixed
- Audio-slide sync issues
- FFmpeg path resolution
- Edge TTS rate limit handling

---

## [1.0.0] - 2024-09-01

### Added
- Initial release
- Tauri desktop application
- FastAPI backend server
- Microsoft Edge TTS integration
- Ollama LLM for prosody tagging
- PowerPoint generation
- English and Hindi language support
- Natural speech with rate/pitch/emphasis
- Deterministic timing estimation
- PostgreSQL job logging

### Features
- Document to presentation conversion
- AI-powered narration with prosody
- Multi-voice selection
- Offline TTS capability
- Desktop app with no terminal required

---

## Version Numbering

- **Major (X.0.0)**: Breaking changes, major features
- **Minor (1.X.0)**: New features, backwards compatible
- **Patch (1.0.X)**: Bug fixes, small improvements

---

## Links

- [GitHub Releases](https://github.com/yourusername/lectra/releases)
- [Documentation](https://github.com/yourusername/lectra/wiki)
- [Issue Tracker](https://github.com/yourusername/lectra/issues)
