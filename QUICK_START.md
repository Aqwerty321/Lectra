# 🚀 Quick Start Guide - Interactive Lecture System

Get your interactive lecture up and running in 5 minutes!

---

## ✅ Prerequisites

- Node.js installed
- Tauri app running
- Backend server on port 8765
- GSAP already in package.json

---

## 📦 Step 1: Verify Installation

Check that GSAP is installed:
```bash
cd ui
npm list gsap
# Should show: gsap@3.13.0
```

If not installed:
```bash
npm install gsap
```

---

## 📁 Step 2: File Structure

Your project should have:
```
LECTRA/
├── ui/src/components/
│   ├── DocumentNotebook.vue (✅ Updated)
│   └── interactive/
│       ├── InteractiveLecture.vue (✅ New)
│       ├── SlideContent.vue (✅ New)
│       ├── AssistantPanel.vue (✅ New)
│       ├── ProgressTracker.vue (✅ New)
│       ├── ConceptSlider.vue (✅ New)
│       └── ConceptToggle.vue (✅ New)
├── sample_data/
│   ├── animations_example.json (✅ Sample)
│   └── timings_example.json (✅ Sample)
└── INTERACTIVE_SYSTEM_GUIDE.md (✅ Full docs)
```

---

## 🎬 Step 3: Test with Sample Data

### Option A: Use Sample Files

1. Copy sample data to your Lectures folder:
```bash
# Windows
mkdir C:\Users\YourUsername\Lectures\sample-lecture
copy sample_data\animations_example.json C:\Users\YourUsername\Lectures\sample-lecture\animations.json
copy sample_data\timings_example.json C:\Users\YourUsername\Lectures\sample-lecture\slide_timings.json
```

2. Add a sample audio file (any MP3):
```bash
copy path\to\any.mp3 C:\Users\YourUsername\Lectures\sample-lecture\narration.mp3
```

### Option B: Use Your Existing Lecture

Make sure your lecture has:
- `narration.mp3`
- `animations.json` (with structure from `animations_example.json`)
- `slide_timings.json` (with structure from `timings_example.json`)

---

## 🎮 Step 4: Launch the App

1. Start the dev server:
```bash
cd ui
npm run tauri:dev
```

2. Navigate to the **🎭 Interactive** tab

3. Select your lecture from the dropdown

4. Click **Play** and enjoy!

---

## ✨ Step 5: Explore Features

### Try These Actions:
1. **Click "Next"** - Advance through bullet points
2. **Click "Ask AI"** - Open the AI assistant
3. **Click highlighted keywords** - See tooltips
4. **Adjust the slider** - Interactive stress level demo
5. **Check badges** - View your achievements
6. **Click "Get Hint"** - Contextual help

---

## 🎨 Step 6: Customize (Optional)

### Change Colors
Edit `InteractiveLecture.vue`:
```css
/* Find and replace */
#654321 → Your primary color
#8b7355 → Your secondary color
#d2b48c → Your accent color
```

### Adjust Speed
In `SlideContent.vue`:
```javascript
duration: 0.6  // Animation speed (seconds)
ease: 'power2.out'  // Easing function
```

### Modify Badges
In `ProgressTracker.vue`:
```javascript
// Change unlock criteria
if (props.hintsUsed >= 5)  // Make it 3 for easier unlock
```

---

## 🐛 Troubleshooting

### Audio Not Playing?
```javascript
// Check browser console (F12)
// Look for: "✅ Audio loaded successfully"

// If you see errors:
1. Verify file path
2. Check convertFileSrc() is used
3. Confirm MP3 format
4. Try different audio file
```

### Animations Not Showing?
```javascript
// Console should show:
// "✅ Found X slides"

// If not:
1. Check animations.json structure
2. Verify slides array exists
3. Confirm steps array populated
```

### Blank Screen?
```javascript
// Check for import errors:
import InteractiveLecture from './interactive/InteractiveLecture.vue'

// Verify path is correct
// Check component is registered
```

---

## 📊 Data Structure Quick Reference

### Minimal animations.json:
```json
{
  "slides": [
    {
      "slide_number": 1,
      "title": "My Slide",
      "start_time": 0,
      "end_time": 10,
      "steps": [
        {
          "element": "bullet",
          "text": "First point",
          "hint": "Optional hint text"
        }
      ]
    }
  ]
}
```

### Minimal timings.json:
```json
{
  "total_duration": 10,
  "slide_timings": [
    {"slide": 1, "start": 0, "end": 10}
  ]
}
```

---

## 🎓 Next Steps

1. **Read Full Guide**: `INTERACTIVE_SYSTEM_GUIDE.md`
2. **Add Interactive Elements**: Sliders, toggles, etc.
3. **Customize Theme**: Colors, fonts, animations
4. **Add More Badges**: Edit `ProgressTracker.vue`
5. **Integrate Backend**: Add `/assistant` endpoint

---

## 💡 Pro Tips

### Keyboard Shortcuts
- `Space` - Play/Pause
- `→` - Next step
- `←` - Previous step
- `H` - Show hint
- `A` - Toggle AI Assistant

### Best Practices
- Keep slides under 20 seconds each
- Use 3-5 bullets per slide
- Add interactive elements every 3-4 slides
- Include hints for complex concepts
- Test on actual users!

### Performance
- Animations auto-cleanup on unmount
- Progress saves to localStorage
- Audio preloads for smooth playback

---

## 🆘 Need Help?

1. Check console logs (F12 in browser)
2. Review `INTERACTIVE_SYSTEM_GUIDE.md`
3. Verify data structures match examples
4. Test with sample data first
5. Check component props are correct

---

## 🎉 Success Checklist

- [ ] GSAP installed
- [ ] All 6 components in `interactive/` folder
- [ ] DocumentNotebook.vue updated with import
- [ ] Sample data copied (optional)
- [ ] App launches without errors
- [ ] Interactive tab loads
- [ ] Lecture plays with animations
- [ ] Buttons work (Next, Hint, Play)
- [ ] AI Assistant opens
- [ ] Badges appear and unlock

---

## 🚀 You're Ready!

Your interactive lecture system is fully operational. Start creating engaging educational experiences!

**Key Features Now Available:**
- ✅ GSAP-powered animations
- ✅ Interactive elements (sliders, toggles)
- ✅ AI Teaching Assistant
- ✅ Gamification & badges
- ✅ Progress tracking
- ✅ Keyword tooltips
- ✅ Contextual hints
- ✅ Beautiful glassmorphism UI

---

**Happy Learning! 🎓✨**
