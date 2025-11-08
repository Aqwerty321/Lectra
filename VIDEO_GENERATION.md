# Video Generation Feature - Documentation

## Overview

LECTRA now automatically generates synced MP4 videos from PowerPoint presentations and narration audio using FFmpeg. The video perfectly synchronizes slide transitions with the narration timing.

## Features

✅ **Automatic Slide Conversion** - PPTX slides converted to high-quality PNG images  
✅ **Perfect Synchronization** - Slides timed to match narration segments  
✅ **Multiple Fallback Methods** - LibreOffice, python-pptx, and placeholder rendering  
✅ **High Quality Output** - Configurable DPI (default: 150) and bitrate  
✅ **Fast Encoding** - H.264 codec with optimized presets  
✅ **Streaming Ready** - MP4 files with faststart flag for web playback  

---

## Prerequisites

### Required: FFmpeg

**Windows Installation:**

1. **Download FFmpeg:**
   - Visit: https://www.gyan.dev/ffmpeg/builds/
   - Download: `ffmpeg-release-essentials.zip`

2. **Extract to C:\ffmpeg:**
   ```powershell
   # Extract the downloaded ZIP
   # Move the 'bin' folder to C:\ffmpeg\bin
   # Result: C:\ffmpeg\bin\ffmpeg.exe
   ```

3. **Verify Installation:**
   ```powershell
   C:\ffmpeg\bin\ffmpeg.exe -version
   ```

**Alternative:** Add FFmpeg to system PATH for global access.

### Optional: LibreOffice (Better Slide Quality)

- **Download:** https://www.libreoffice.org/download/
- **Install to:** `C:\Program Files\LibreOffice\`
- **Benefits:** Higher quality slide rendering vs. placeholder images

---

## How It Works

### Pipeline Overview

```
PPTX File
    ↓
[1] Convert slides to PNG images (150 DPI)
    ↓
[2] Load slide timing data (slide_timings.json)
    ↓
[3] Create FFmpeg concat file with durations
    ↓
[4] Encode video with H.264 + AAC
    ↓
MP4 Video (synced slides + audio)
```

### Slide Conversion Methods (Priority Order)

1. **python-pptx + Pillow** (Built-in, fast)
   - Renders slides directly from PPTX
   - Quality: Good for simple slides
   - Speed: Fast (~1s per slide)

2. **LibreOffice CLI** (Optional, best quality)
   - Converts PPTX → PDF → PNG
   - Quality: Excellent, preserves formatting
   - Speed: Moderate (~3s per slide)
   - Requires: LibreOffice installed

3. **Placeholder Images** (Fallback)
   - Creates gradient backgrounds with slide numbers
   - Quality: Basic, for testing only
   - Speed: Very fast

### FFmpeg Video Encoding

```bash
ffmpeg -f concat -safe 0 -i concat.txt \
       -i narration.mp3 \
       -c:v libx264 \
       -pix_fmt yuv420p \
       -crf 23 \
       -preset medium \
       -c:a aac \
       -b:a 192k \
       -shortest \
       -movflags +faststart \
       presentation_video.mp4
```

**Parameters Explained:**
- `-f concat`: Use concat demuxer for image sequence with durations
- `-c:v libx264`: H.264 video codec (universal compatibility)
- `-pix_fmt yuv420p`: Pixel format for max compatibility
- `-crf 23`: Quality (18=high, 28=low, 23=balanced)
- `-preset medium`: Encoding speed vs compression
- `-c:a aac`: AAC audio codec
- `-b:a 192k`: Audio bitrate (192 kbps)
- `-shortest`: Match video length to audio
- `-movflags +faststart`: Enable streaming playback

---

## API Usage

### Generate Presentation with Video

```python
POST /generate_presentation
```

**Request Body:**
```json
{
  "project": "my-presentation",
  "topic": "Artificial Intelligence in Healthcare",
  "lang": "en",
  "voice": "en-US-AriaNeural",
  "fallback_rate": "-10%",
  "fallback_pitch": "+0st",
  "generate_video": true  // <-- Enable video generation
}
```

**Response:**
```json
{
  "status": "ok",
  "project_dir": "C:\\Users\\...\\Lectures\\my-presentation",
  "presentation_title": "Artificial Intelligence in Healthcare",
  "slide_count": 10,
  "image_count": 8,
  "pptx_path": "C:\\Users\\...\\presentation.pptx",
  "audio_path": "C:\\Users\\...\\narration.mp3",
  "video_path": "C:\\Users\\...\\presentation_video.mp4",  // <-- Video path
  "duration_sec": 180.5,
  "features": [
    "AI-generated content",
    "Professional design",
    "Auto-fetched images",
    "Charts & diagrams",
    "Synchronized narration",
    "MP4 video with synced slides"  // <-- Video feature
  ]
}
```

### Disable Video Generation

Set `generate_video: false` to skip video creation (faster, PPTX + audio only).

---

## File Structure

After generation, your project directory contains:

```
C:\Users\<username>\Lectures\<project>\
├── presentation.pptx           # PowerPoint file
├── narration.mp3               # Audio narration
├── narration.txt               # Original narration text
├── narration_tagged.txt        # Tagged text with prosody
├── slide_timings.json          # Slide timing data
├── presentation_video.mp4      # 🎬 SYNCED VIDEO (NEW!)
└── slide_images/               # Extracted slide PNGs
    ├── slide_001.png
    ├── slide_002.png
    ├── slide_003.png
    └── ...
```

---

## Configuration Options

### In Code (video_generator.py)

```python
video_path = generate_presentation_video(
    pptx_path=Path("presentation.pptx"),
    audio_path=Path("narration.mp3"),
    slide_timings_path=Path("slide_timings.json"),
    output_dir=Path("output"),
    output_name="my_video.mp4",
    dpi=150,        # Image quality (96-300)
    fps=30          # Frames per second (24-60)
)
```

### Quality Settings

| DPI | Quality | File Size | Use Case |
|-----|---------|-----------|----------|
| 96  | Low     | Small     | Quick preview |
| 150 | Good    | Medium    | **Default - balanced** |
| 200 | High    | Large     | Professional output |
| 300 | Very High | Very Large | Print quality |

| CRF | Quality | Encoding Time | Use Case |
|-----|---------|---------------|----------|
| 18  | Excellent | Slow        | Archival, professional |
| 23  | Good      | Medium      | **Default - balanced** |
| 28  | Acceptable | Fast       | Quick preview |

---

## Troubleshooting

### Error: "FFmpeg not found"

**Solution:**
```powershell
# Check if FFmpeg exists
Test-Path C:\ffmpeg\bin\ffmpeg.exe

# If False, reinstall FFmpeg to C:\ffmpeg
```

### Error: "Failed to convert PPTX to images"

**Solution 1:** Install LibreOffice
- Download: https://www.libreoffice.org/download/
- Install with default settings

**Solution 2:** Check python-pptx
```powershell
pip install python-pptx Pillow --upgrade
```

### Video Quality Issues

**Blurry slides:**
```python
# Increase DPI in video_generator.py
dpi=200  # or 300 for very high quality
```

**Large file size:**
```python
# Increase CRF (lower quality, smaller file)
crf=28  # instead of default 23
```

**Choppy playback:**
```python
# Increase FPS
fps=60  # instead of default 30
```

### Slide Timing Issues

**Slides change too quickly/slowly:**

Check `slide_timings.json`:
```json
{
  "total_duration": 180.5,
  "slides": [
    {
      "slide_number": 1,
      "title": "Introduction",
      "start_time": 0.0,
      "end_time": 15.5,
      "duration": 15.5  // <-- Adjust if needed
    }
  ]
}
```

The timings are calculated from audio narration length. If incorrect:
1. Check speaker notes in PPTX (longer notes = longer slide time)
2. Regenerate presentation with adjusted narration

---

## Performance

### Typical Generation Times (10-slide presentation)

| Step | Time | Notes |
|------|------|-------|
| Slide rendering (python-pptx) | 10s | Fast, basic quality |
| Slide rendering (LibreOffice) | 30s | Slower, best quality |
| FFmpeg encoding | 5-15s | Depends on duration |
| **Total** | **15-45s** | Full pipeline |

### Optimization Tips

1. **Use python-pptx rendering** (default) for faster generation
2. **Lower DPI** (96-120) for quick previews
3. **Disable video** during development (`generate_video: false`)
4. **Install LibreOffice** only for production/final videos

---

## Advanced Usage

### Custom FFmpeg Parameters

Edit `video_generator.py` > `create_video_from_slides()`:

```python
video_cmd = [
    ffmpeg_path,
    '-f', 'concat',
    '-safe', '0',
    '-i', str(concat_file),
    '-i', str(audio_path),
    '-c:v', 'libx264',
    '-crf', '20',          # <-- Change quality
    '-preset', 'slow',     # <-- Change speed/compression
    '-tune', 'stillimage', # <-- Optimize for static images
    '-c:a', 'aac',
    '-b:a', '256k',        # <-- Change audio bitrate
    '-movflags', '+faststart',
    '-y',
    str(output_path)
]
```

### Batch Processing

```python
from pathlib import Path
from app.services.video_generator import generate_presentation_video

projects = [
    ("project1", "AI in Healthcare"),
    ("project2", "Climate Change"),
    ("project3", "Space Exploration")
]

for project, topic in projects:
    project_dir = Path(f"C:/Users/.../Lectures/{project}")
    
    video_path = generate_presentation_video(
        pptx_path=project_dir / "presentation.pptx",
        audio_path=project_dir / "narration.mp3",
        slide_timings_path=project_dir / "slide_timings.json",
        output_dir=project_dir
    )
    
    print(f"✅ {topic}: {video_path}")
```

---

## Technical Details

### Concat File Format

FFmpeg concat demuxer file (`concat.txt`):

```
file 'C:/path/to/slide_001.png'
duration 15.5
file 'C:/path/to/slide_002.png'
duration 18.2
file 'C:/path/to/slide_003.png'
duration 12.8
file 'C:/path/to/slide_003.png'
```

**Note:** Last image is repeated (FFmpeg concat requirement).

### Video Specifications

- **Container:** MP4 (H.264 + AAC)
- **Video Codec:** libx264 (H.264)
- **Audio Codec:** AAC
- **Resolution:** Based on slide size (typically 1920x1080 @ 150 DPI)
- **Aspect Ratio:** 16:9 (from PPTX dimensions)
- **Framerate:** 30 fps (configurable)
- **Video Bitrate:** Variable (CRF-based)
- **Audio Bitrate:** 192 kbps (configurable)
- **Compatibility:** All major browsers, media players, mobile devices

---

## Future Enhancements

🔮 **Planned Features:**

1. **Transition Effects** - Fade, dissolve between slides
2. **Subtitle Overlay** - Burned-in captions from timing data
3. **Progress Bar** - Visual progress indicator
4. **Branding** - Watermark/logo overlay
5. **Resolution Presets** - 720p, 1080p, 4K options
6. **Thumbnail Generation** - Video preview image
7. **Chapter Markers** - MP4 chapters for each slide
8. **VP9/HEVC Support** - Alternative codecs for smaller files

---

## Credits

- **FFmpeg:** https://ffmpeg.org/ (Video encoding)
- **python-pptx:** https://python-pptx.readthedocs.io/ (PPTX parsing)
- **Pillow:** https://pillow.readthedocs.io/ (Image processing)
- **LibreOffice:** https://www.libreoffice.org/ (Optional slide rendering)

---

*Generated by LECTRA - Lecture TTS with Realistic Audio*  
*Feature added: November 2025*
