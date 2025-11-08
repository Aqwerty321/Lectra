# 🎓 Interactive Study Mode - Feature Documentation

## Overview
Interactive Study Mode transforms passive video watching into an active learning experience by integrating AI-generated quizzes at strategic intervals throughout the presentation.

## Key Features

### 1. **Smart Quiz Generation** 🧠
- AI-powered MCQ generation using Ollama (llama3.2:3b)
- Questions based on actual slide content via RAG
- 5 questions per quiz checkpoint
- Three difficulty levels: Easy 🌱, Medium 🌿, Hard 🌳

### 2. **Video-Quiz Integration** 🎬
- Video automatically pauses at quiz checkpoints
- Visual overlay indicates quiz is active
- Video resumes only after quiz completion
- Configurable quiz frequency (every 2-5 slides)

### 3. **Interactive Learning** 📝
- Multiple choice questions (4 options: A, B, C, D)
- Hint system available for each question
- Immediate feedback on answers
- Detailed explanations for correct/incorrect options
- Color-coded feedback (green = correct, red = incorrect)

### 4. **Progress Tracking** 📊
- Real-time score display
- Accuracy percentage calculation
- Session duration timer
- Quiz completion counter
- Persistent progress storage

### 5. **Adaptive Difficulty** 🎯
- Choose difficulty before starting session
- Hints available without penalty
- Comprehensive explanations for learning
- Review mode for missed questions

## User Flow

```
┌─────────────────────────────────────┐
│  1. Select Project & Settings       │
│     - Choose presentation           │
│     - Set quiz frequency            │
│     - Select difficulty             │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  2. Watch Video (Slides 1-3)        │
│     - Video plays normally          │
│     - Track current slide           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  3. Quiz Checkpoint                 │
│     ⏸️  Video pauses automatically  │
│     📝 5 MCQs generated             │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  4. Answer Questions                │
│     - Read question                 │
│     - Request hint (optional)       │
│     - Select answer                 │
│     - View feedback & explanation   │
│     - Next question                 │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  5. Quiz Complete                   │
│     - View score (X/5)              │
│     - Resume video button           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  6. Continue or Complete            │
│     - If more checkpoints: goto 2   │
│     - If done: Session Complete 🎓  │
└─────────────────────────────────────┘
```

## Technical Implementation

### Backend Components

#### 1. **Quiz Generator Service** (`quiz_generator.py`)
```python
class QuizGenerator:
    - generate_mcqs(): Creates MCQs using Ollama
    - generate_quiz_checkpoints(): Calculates quiz intervals
    - _build_quiz_prompt(): Crafts AI prompts
    - _parse_mcqs(): Validates quiz structure
```

#### 2. **API Endpoints** (`api.py`)
- `POST /generate_quiz`: Generate quiz for slide range
- `GET /get_quiz_checkpoints`: Get quiz checkpoint positions
- `POST /submit_quiz_answer`: Validate answer and get feedback

#### 3. **Data Storage**
- `quiz_cache.json`: Cached generated quizzes per project
- `study_progress.json`: User answers and scores
- `metadata.json`: Slide content and structure

### Frontend Components

#### 1. **InteractiveStudyMode.vue**
Main component managing the study session:
- Session initialization and configuration
- Video playback control
- Quiz state management
- Progress tracking
- Analytics display

#### 2. **State Management**
```javascript
studySession: {
  total_slides, checkpoints, checkpoint_interval
}
quizMode: boolean (video paused/active quiz)
currentQuiz: { questions, difficulty, slide_range }
progress: { score, accuracy, duration }
```

### Data Flow

```
User Action → Frontend Request → Backend API → Ollama LLM
                                      ↓
                                Quiz Generation
                                      ↓
                                Cache Storage
                                      ↓
Frontend ← JSON Response ← Validated MCQs
```

## Quiz Question Structure

```json
{
  "question": "What is the main concept?",
  "options": {
    "A": "Option 1",
    "B": "Option 2",
    "C": "Option 3",
    "D": "Option 4"
  },
  "correct_answer": "B",
  "explanation": "B is correct because... A/C/D are wrong because...",
  "hint": "Think about the key relationship",
  "difficulty": "medium",
  "slide_reference": 2
}
```

## Configuration Options

### Quiz Frequency
- **Every 2 slides**: Intensive learning (more quizzes)
- **Every 3 slides**: Balanced (default)
- **Every 4 slides**: Moderate review
- **Every 5 slides**: Light reinforcement

### Difficulty Levels
- **Easy 🌱**: Basic recall, simple concepts
- **Medium 🌿**: Understanding and application (default)
- **Hard 🌳**: Analysis, synthesis, critical thinking

## Analytics & Metrics

### Real-time Display
- **Quizzes Done**: Number of completed checkpoints
- **Correct Answers**: Total correct responses
- **Accuracy %**: (Correct / Total) × 100
- **Study Time**: Session duration (mm:ss)

### Session Complete Stats
- Total quizzes completed
- Final accuracy percentage
- Total study time
- Detailed progress history

## Learning Features

### 1. **Hint System** 💡
- Available before answering
- No score penalty
- Guides thinking without revealing answer
- Contextual to question content

### 2. **Explanations** 📚
- Shown after answering
- Explains why correct answer is right
- Explains why each wrong answer is incorrect
- Reinforces learning concepts

### 3. **Visual Feedback** 🎨
- Green highlight: Correct answer
- Red highlight: Incorrect answer
- Checkmark: Success
- X mark: Try again
- Progress bars and scores

### 4. **Adaptive Pacing** ⏱️
- User controls quiz speed
- No time pressure on questions
- Can review explanations thoroughly
- Pause/resume at checkpoints

## User Experience Highlights

### Session Start
1. Beautiful purple gradient UI
2. Clear project selection
3. Intuitive settings (frequency, difficulty)
4. Single "Start Study Session" button

### During Quiz
- Video dims/pauses automatically
- Large, readable question text
- Clear option buttons (A, B, C, D)
- Accessible hint button
- Instant feedback on submission

### Session Complete
- Celebratory UI (🎓 emoji, stats)
- Final score display
- Accuracy breakdown
- "Start New Session" button

## Technical Notes

### Performance
- Quizzes cached to avoid regeneration
- Ollama generates 5 questions in ~10-15 seconds
- Video playback unaffected by quiz loading
- Progress saved incrementally

### Error Handling
- Fallback MCQs if Ollama fails
- Graceful degradation
- User-friendly error messages
- Automatic retry logic

### Security
- Tauri's convertFileSrc for video paths
- Asset scope limited to Lectures folder
- No external network calls (except Ollama)
- Progress data stored locally

## Future Enhancements (Potential)

1. **Spaced Repetition**: Review missed questions later
2. **Leaderboards**: Compare scores with friends
3. **Custom Quiz Creation**: Manual quiz authoring
4. **Export Progress**: PDF/CSV reports
5. **Adaptive Difficulty**: Auto-adjust based on performance
6. **Voice Questions**: Text-to-speech for questions
7. **Multi-language**: Quiz translation
8. **Gamification**: Badges, streaks, achievements

## Usage Instructions

### For Users:
1. Generate a presentation with video
2. Click "🎓 Study Mode" tab
3. Select project from dropdown
4. Configure quiz frequency and difficulty
5. Click "🚀 Start Study Session"
6. Watch video and answer quizzes
7. Review final stats

### For Developers:
1. Backend requires Ollama running (llama3.2:3b)
2. Frontend uses Vue 3 + Tauri
3. Quiz data cached in project folder
4. Modify `quiz_generator.py` for prompt tuning
5. Adjust checkpoint intervals in settings

## Comparison: Old vs New

### Before (Simple Viewer)
- ❌ Passive video watching
- ❌ No engagement tracking
- ❌ No learning verification
- ❌ One-way information flow

### After (Interactive Study Mode)
- ✅ Active learning with quizzes
- ✅ Progress tracking & analytics
- ✅ Immediate feedback & explanations
- ✅ Two-way interactive experience
- ✅ Customizable difficulty & frequency
- ✅ Hints & learning support
- ✅ Persistent progress storage

## Conclusion

Interactive Study Mode transforms LECTRA from a presentation generator into a comprehensive learning platform. By combining video content with AI-generated quizzes, it creates an engaging, effective study experience that promotes active learning and retention.

The feature seamlessly integrates with existing workflows while adding significant educational value through intelligent quiz generation, adaptive difficulty, and detailed progress tracking.

---

**Status**: ✅ Fully Implemented
**Components**: 3 new files (quiz_generator.py, InteractiveStudyMode.vue, STUDY_MODE_GUIDE.md)
**API Endpoints**: 3 new endpoints
**Lines of Code**: ~1,000+
**Testing Required**: Yes (Ollama integration, video sync, quiz generation)
