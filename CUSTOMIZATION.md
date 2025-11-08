# 🎨 LECTRA Customization Guide

## Quick Customizations (No Coding Required)

### 1. Change System Prompt (Adjust Speech Style)

**File**: `sidecar\app\services\nuance_system_prompt.txt`

**Current**: Aggressive teacher style with 70-80% tagged sentences

**To make more natural**:
- Reduce tag frequency from "70-80%" to "40-50%"
- Reduce rate range from "-30% to +25%" to "-15% to +15%"
- Keep pause rules the same (they're critical)

**To make more dramatic**:
- Increase pitch range from "±2st" to "±3st"
- Add more excitement patterns: "[rate=+30%] [pitch=+3st]"
- Increase pause ranges: "[pause=1500-2000ms]"

### 2. Add More Sample Texts

**File**: `sidecar\app\services\samples.py`

```python
# Add new sample (copy pattern from EN_SAMPLE):
JA_SAMPLE = """
<Your Japanese text here in full-width characters>
"""

# Then update api.py to handle "ja" in use_sample
```

**Don't forget**: Update `GeneratorPanel.vue` to add a button for new language!

### 3. Change Default Voices

**File**: `.env`

```env
# Change these to any EdgeTTS voice
DEFAULT_EN_VOICE=en-GB-RyanNeural     # British English male
DEFAULT_HI_VOICE=hi-IN-MadhurNeural   # Hindi male

# See all voices at: https://speech.microsoft.com/portal/voicegallery
```

### 4. Change Output Directory

**File**: `.env`

```env
# Windows
OUTPUT_ROOT=C:\MyLectures

# Or relative to user
OUTPUT_ROOT=~/Documents/Lectures
```

### 5. Adjust Timing Formula

**File**: `sidecar\app\services\timing.py`

**To make timing faster** (increase WPM):
```python
# Line ~74
BASE_WPM = {
    "en": 180,  # was 165
    "hi": 165,  # was 150
}
```

**To add pauses for punctuation**:
```python
# Line ~103
punct_ms = (
    punct['comma'] * 300 +        # was 200
    (punct['period'] + ...) * 600 # was 450
)
```

---

## UI Customizations

### 6. Change Color Scheme

**File**: `ui\src\styles.css`

**Replace wood backgrounds with gradients**:
```css
.bg-darkest-wood {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.bg-dark-wood {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.bg-light-wood {
  background: linear-gradient(135deg, #fdfcfb 0%, #e2d1c3 100%);
}
```

**Change glassmorphism opacity** (line ~22):
```css
.glass-card {
  @apply bg-white/95 backdrop-blur-xl;  /* was /90 */
}
```

### 7. Add More Voices to Dropdown

**File**: `ui\src\components\GeneratorPanel.vue`

Around line 53, in the `<select>` element:
```vue
<optgroup label="English Voices">
  <option value="en-US-GuyNeural">en-US-GuyNeural (Male)</option>
  <option value="en-US-AriaNeural">en-US-AriaNeural (Female)</option>
  <!-- ADD MORE HERE -->
  <option value="en-GB-RyanNeural">en-GB-RyanNeural (British Male)</option>
  <option value="en-AU-NatashaNeural">en-AU-NatashaNeural (Australian Female)</option>
</optgroup>
```

### 8. Change Font

**File**: `ui\tailwind.config.cjs`

```js
theme: {
  extend: {
    fontFamily: {
      'sans': ['Poppins', 'Inter', 'system-ui', 'sans-serif'],  // was Modulus
    }
  }
}
```

Then import the font in `ui\src\styles.css`:
```css
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
```

### 9. Customize Feature Cards

**File**: `ui\src\components\FeatureCards.vue`

```js
const features = [
  {
    icon: '🎯',
    title: 'Your Feature',
    description: 'Your description here'
  },
  // Add more or modify existing...
]
```

### 10. Change App Window Size

**File**: `tauri.conf.json`

Around line 58:
```json
"windows": [
  {
    "width": 1400,    // was 1200
    "height": 1000,   // was 900
    "minWidth": 1000, // was 800
    "minHeight": 700  // was 600
  }
]
```

---

## Advanced Customizations (Coding Required)

### 11. Add Audio Playback In-App

**File**: `ui\src\components\GeneratorPanel.vue`

Replace the `playAudio` function (line ~157):
```vue
<script setup>
// Add at top
import { open } from '@tauri-apps/api/shell'

// Replace playAudio function
async function playAudio(path) {
  try {
    await open(path)  // Opens with default app
    emit('status', 'Playing audio...', 'info')
  } catch (err) {
    emit('status', `Failed to play: ${err}`, 'error')
  }
}
</script>
```

### 12. Add Progress Streaming

Instead of fake progress bar, stream real updates from sidecar:

**Backend** (`sidecar\app\api.py`):
```python
from fastapi.responses import StreamingResponse
import asyncio

@app.post("/generate_stream")
async def generate_lecture_stream(request: GenerateRequest):
    async def event_stream():
        yield f"data: {json.dumps({'progress': 10, 'message': 'Starting tagging...'})}\n\n"
        # ... generate tagged text ...
        yield f"data: {json.dumps({'progress': 40, 'message': 'Generating audio...'})}\n\n"
        # ... rest of pipeline ...
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

**Frontend** (`ui\src\components\GeneratorPanel.vue`):
```js
// Use EventSource for SSE
const eventSource = new EventSource('http://127.0.0.1:8765/generate_stream')
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data)
  progressMessage.value = data.message
  // Update real progress bar
}
```

### 13. Add Batch Processing

**Backend** (`sidecar\app\api.py`):
```python
class BatchRequest(BaseModel):
    projects: List[Dict[str, Any]]  # List of GenerateRequest dicts

@app.post("/batch_generate")
async def batch_generate(request: BatchRequest):
    results = []
    for project_data in request.projects:
        # Generate each project
        result = await generate_lecture(GenerateRequest(**project_data))
        results.append(result)
    return {"results": results}
```

**Frontend**: Add a "Batch" tab with file upload or multi-project form.

### 14. Implement PowerPoint Sync

**File**: `sidecar\app\services\ppt_sync.py`

```python
from pptx import Presentation

def map_cues(timings: Dict, slides_pptx: Path) -> Dict:
    """Map timing cues to PPT bullets."""
    prs = Presentation(str(slides_pptx))
    
    cues = {"slides": []}
    sentence_idx = 0
    
    for slide_num, slide in enumerate(prs.slides, 1):
        slide_data = {"slide_num": slide_num, "bullets": []}
        
        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    text = paragraph.text.strip()
                    if text and sentence_idx < len(timings['sentences']):
                        timing = timings['sentences'][sentence_idx]
                        slide_data["bullets"].append({
                            "text": text,
                            "start": timing['start'],
                            "end": timing['end']
                        })
                        sentence_idx += 1
        
        cues["slides"].append(slide_data)
    
    return cues
```

Add to requirements.txt:
```txt
python-pptx>=0.6.21
```

### 15. Add Voice Preview

**Frontend** (`ui\src\components\GeneratorPanel.vue`):

Add button next to voice dropdown:
```vue
<button
  @click="previewVoice"
  class="ml-2 px-3 py-2 bg-blue-500 text-white rounded"
>
  🔊 Preview
</button>

<script setup>
async function previewVoice() {
  const testText = lang.value === 'hi' 
    ? 'नमस्ते, यह एक परीक्षण है।'
    : 'Hello, this is a voice preview.'
  
  const response = await fetch('http://127.0.0.1:8765/preview_voice', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text: testText,
      voice: voice.value || (lang.value === 'hi' ? 'hi-IN-SwaraNeural' : 'en-US-GuyNeural')
    })
  })
  
  const blob = await response.blob()
  const audio = new Audio(URL.createObjectURL(blob))
  audio.play()
}
</script>
```

**Backend** (`sidecar\app\api.py`):
```python
from fastapi.responses import FileResponse

@app.post("/preview_voice")
async def preview_voice(request: dict):
    # Generate short audio sample
    temp_file = Path(tempfile.mktemp(suffix='.mp3'))
    
    communicate = edge_tts.Communicate(
        text=request['text'],
        voice=request['voice']
    )
    await communicate.save(str(temp_file))
    
    return FileResponse(str(temp_file), media_type='audio/mpeg')
```

---

## Configuration Tweaks

### 16. Change Ollama Model

**File**: `sidecar\app\config.py`

```python
OLLAMA_MODEL = "llama3.2:latest"  # was llama3.1:latest
# Or try: "mistral:latest", "codellama:latest"
```

**Note**: Make sure to pull the model first:
```powershell
ollama pull llama3.2:latest
```

### 17. Adjust Ollama Generation Parameters

**File**: `sidecar\app\services\ollama_client.py`

Around line 28:
```python
"options": {
    "temperature": 0.3,      # was 0.1 (more creative)
    "top_p": 0.9,            # was 0.8
    "repeat_penalty": 1.1,   # was 1.05
    "num_ctx": 8192          # was 4096 (more context)
}
```

### 18. Enable Database Logging

**File**: `.env`

```env
# Install PostgreSQL, create database "lectra", then:
DATABASE_URL=postgresql://username:password@localhost:5432/lectra
```

**File**: `sidecar\app\services\postgres.py` already has table creation!

View logs:
```sql
SELECT * FROM jobs ORDER BY created_at DESC LIMIT 10;
```

### 19. Change Sidecar Port

**File**: `tauri.conf.json`

Around line 14:
```json
"scope": [
  {
    "name": "lecture-sidecar",
    "sidecar": true,
    "args": ["--port", "9000"]  // was 8765
  }
]
```

**Also update** all `fetch()` calls in Vue components from `:8765` to `:9000`.

### 20. Add More Languages

**Files to edit**:

1. **`sidecar\app\services\samples.py`**: Add sample text
2. **`sidecar\app\config.py`**: Add BASE_WPM entry
3. **`ui\src\components\GeneratorPanel.vue`**: Add language button
4. **`ui\src\components\HeroLogo.vue`**: Add CTA button

Example for Spanish:
```python
# samples.py
ES_SAMPLE = """
El aprendizaje automático es una rama de la inteligencia artificial...
"""

# config.py
BASE_WPM = {
    "en": 165,
    "hi": 150,
    "es": 170,  # Add Spanish
}

DEFAULT_ES_VOICE = "es-ES-AlvaroNeural"
```

---

## Testing Customizations

After making changes:

### If you changed Python code:
```powershell
# Rebuild sidecar
cd C:\edgettstest\LECTRA
.\scripts\build_sidecar.ps1

# Or run directly without rebuild (dev):
cd sidecar
python -m app.api
```

### If you changed UI code:
```powershell
# Vite auto-reloads in dev mode
# Or restart:
cd C:\edgettstest\LECTRA\ui
npm run tauri dev
```

### Full rebuild:
```powershell
# Clean everything
cd C:\edgettstest\LECTRA
Remove-Item -Recurse -Force ui\node_modules, ui\dist, ui\src-tauri\target

# Rebuild from scratch
.\scripts\build_sidecar.ps1
cd ui
npm install
npm run tauri build
```

---

## Common Pitfall Fixes

### Issue: Changes not applying

**Solution**: Clear caches
```powershell
# Python cache
cd sidecar
Remove-Item -Recurse -Force __pycache__, app\__pycache__, app\services\__pycache__

# Node cache
cd ..\ui
Remove-Item -Recurse -Force node_modules, dist
npm install

# Rust cache
cd src-tauri
cargo clean
```

### Issue: Sidecar not restarting

**Solution**: Kill manually and restart
```powershell
# Find process
Get-Process | Where-Object {$_.ProcessName -like "*lecture-sidecar*"}

# Kill it
Stop-Process -Name "lecture-sidecar" -Force

# Restart app
npm run tauri dev
```

### Issue: Timings are wrong

**Solution**: Recalibrate WPM values
1. Generate audio with known text
2. Measure actual duration with media player
3. Calculate: `actual_wpm = (word_count / duration_sec) * 60`
4. Update `BASE_WPM` in `config.py`

---

## Best Practices

1. **Test incrementally**: Make one change, test, commit
2. **Keep backups**: Copy working files before modifying
3. **Use dev mode**: Much faster iteration than full builds
4. **Check logs**: Console shows useful error messages
5. **Version control**: Git commit after each working change

---

## Resources

- **EdgeTTS Voices**: https://speech.microsoft.com/portal/voicegallery
- **Ollama Models**: https://ollama.ai/library
- **Tailwind CSS**: https://tailwindcss.com/docs
- **Vue 3 Docs**: https://vuejs.org/guide/
- **Tauri Docs**: https://tauri.app/v1/guides/

---

**Happy Customizing! 🎨**

If you make something cool, share it with Team Just-Git-Gud! ❤️
