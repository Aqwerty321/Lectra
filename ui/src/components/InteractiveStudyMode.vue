<template>
  <div class="study-mode bg-gradient-to-br from-purple-50 to-indigo-50 rounded-2xl shadow-2xl p-8">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-3xl font-bold text-purple-900">🎓 Interactive Study Mode</h2>
        <p class="text-sm text-purple-600 mt-1">Learn with AI-powered quizzes</p>
      </div>
      <div v-if="studySession" class="text-right">
        <div class="text-sm text-gray-600">Progress</div>
        <div class="text-2xl font-bold text-purple-700">
          {{ currentCheckpoint + 1 }} / {{ totalCheckpoints }}
        </div>
      </div>
    </div>

    <!-- Project Selector (if no active session) -->
    <div v-if="!studySession" class="bg-white rounded-xl p-6 shadow-lg">
      <h3 class="text-xl font-semibold text-purple-900 mb-4">📚 Start Study Session</h3>
      
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">Select Project</label>
        <select
          v-model="selectedProject"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
        >
          <option value="">-- Choose a project --</option>
          <option
            v-for="project in projects.filter(p => p.has_video)"
            :key="project.name"
            :value="project.name"
          >
            {{ project.name }}
          </option>
        </select>
      </div>

      <div class="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Quiz Frequency</label>
          <select
            v-model="checkpointInterval"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
          >
            <option :value="2">Every 2 slides</option>
            <option :value="3">Every 3 slides</option>
            <option :value="4">Every 4 slides</option>
            <option :value="5">Every 5 slides</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Difficulty</label>
          <select
            v-model="difficulty"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
          >
            <option value="easy">Easy 🌱</option>
            <option value="medium">Medium 🌿</option>
            <option value="hard">Hard 🌳</option>
          </select>
        </div>
      </div>

      <button
        @click="startStudySession"
        :disabled="!selectedProject || loading"
        class="w-full py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
      >
        {{ loading ? '⏳ Loading...' : '🚀 Start Study Session' }}
      </button>
    </div>

    <!-- Active Study Session -->
    <div v-if="studySession && !sessionComplete" class="space-y-6">
      <!-- Video Player Section -->
      <div class="bg-white rounded-xl p-6 shadow-lg">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-purple-900">
            {{ quizMode ? '⏸️ Video Paused - Quiz Time!' : '▶️ Video Playing' }}
          </h3>
          <div class="flex gap-2">
            <span class="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium">
              Slide {{ currentSlide + 1 }} / {{ totalSlides }}
            </span>
            <span v-if="quizMode" class="px-3 py-1 bg-amber-100 text-amber-700 rounded-full text-sm font-medium animate-pulse">
              Quiz Active
            </span>
          </div>
        </div>

        <!-- Video Player -->
        <div class="relative">
          <video
            ref="videoPlayer"
            :key="videoPath"
            @timeupdate="onVideoTimeUpdate"
            @ended="onVideoEnded"
            controls
            :class="{'opacity-30 pointer-events-none': quizMode}"
            class="w-full rounded-lg shadow-lg transition-opacity"
            style="max-height: 500px;"
          >
            <source :src="videoSrc" type="video/mp4" />
            Your browser does not support the video tag.
          </video>
          
          <!-- Quiz Overlay -->
          <div v-if="quizMode" class="absolute inset-0 flex items-center justify-center bg-black bg-opacity-40 rounded-lg">
            <div class="bg-white px-6 py-3 rounded-lg shadow-xl">
              <p class="text-lg font-semibold text-purple-900">📝 Complete the quiz to continue</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Quiz Section -->
      <div v-if="quizMode" class="bg-white rounded-xl p-6 shadow-lg">
        <!-- Loading State -->
        <div v-if="!currentQuiz && loading" class="text-center py-12">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-purple-500 border-t-transparent mb-4"></div>
          <p class="text-lg font-semibold text-purple-900">Generating Quiz...</p>
          <p class="text-sm text-gray-600 mt-2">Using AI to create personalized questions</p>
        </div>
        
        <!-- Quiz Content -->
        <div v-else-if="currentQuiz">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-xl font-semibold text-purple-900">
              📝 Quiz {{ currentCheckpoint + 1 }}
            </h3>
            <div class="text-sm text-gray-600">
              Score: <span class="font-bold text-purple-700">{{ quizScore }} / {{ answeredQuestions }}</span>
            </div>
          </div>

        <!-- Current Question -->
        <div v-if="currentQuiz.questions && currentQuestionIndex < currentQuiz.questions.length">
          <div class="mb-6">
            <div class="flex items-center justify-between mb-3">
              <span class="text-sm font-medium text-gray-600">
                Question {{ currentQuestionIndex + 1 }} of {{ currentQuiz.questions.length }}
              </span>
              <span class="px-3 py-1 rounded-full text-xs font-medium"
                    :class="{
                      'bg-green-100 text-green-700': currentQuiz.difficulty === 'easy',
                      'bg-yellow-100 text-yellow-700': currentQuiz.difficulty === 'medium',
                      'bg-red-100 text-red-700': currentQuiz.difficulty === 'hard'
                    }">
                {{ currentQuiz.difficulty }}
              </span>
            </div>

            <div class="bg-purple-50 p-4 rounded-lg mb-4">
              <p class="text-lg text-gray-800 font-medium">
                {{ currentQuestion.question }}
              </p>
            </div>

            <!-- Options -->
            <div class="space-y-3">
              <button
                v-for="(text, option) in currentQuestion.options"
                :key="option"
                @click="selectAnswer(option)"
                :disabled="answerSubmitted"
                :class="getOptionClass(option)"
                class="w-full text-left px-4 py-3 rounded-lg border-2 transition-all font-medium"
              >
                <span class="font-bold">{{ option }}.</span> {{ text }}
              </button>
            </div>

            <!-- Hint Button -->
            <div v-if="!answerSubmitted && !hintShown" class="mt-4">
              <button
                @click="showHint"
                class="text-purple-600 hover:text-purple-800 text-sm font-medium"
              >
                💡 Need a hint?
              </button>
            </div>

            <!-- Hint Display -->
            <div v-if="hintShown && !answerSubmitted" class="mt-4 p-3 bg-blue-50 border-l-4 border-blue-400 rounded">
              <p class="text-sm text-blue-800">
                <span class="font-semibold">💡 Hint:</span> {{ currentQuestion.hint }}
              </p>
            </div>

            <!-- Answer Feedback -->
            <div v-if="answerSubmitted" class="mt-4">
              <div v-if="answerFeedback.is_correct" class="p-4 bg-green-50 border-l-4 border-green-500 rounded">
                <p class="text-green-800 font-semibold mb-2">✅ Correct!</p>
                <p class="text-sm text-green-700">{{ answerFeedback.explanation }}</p>
              </div>
              <div v-else class="p-4 bg-red-50 border-l-4 border-red-500 rounded">
                <p class="text-red-800 font-semibold mb-2">❌ Incorrect</p>
                <p class="text-sm text-red-700 mb-2">
                  The correct answer was <span class="font-bold">{{ answerFeedback.correct_answer }}</span>
                </p>
                <p class="text-sm text-red-700">{{ answerFeedback.explanation }}</p>
              </div>

              <button
                @click="nextQuestion"
                class="mt-4 w-full py-2 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition-all"
              >
                {{ currentQuestionIndex < currentQuiz.questions.length - 1 ? '➡️ Next Question' : '🎉 Finish Quiz' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Quiz Complete -->
        <div v-else-if="currentQuiz.questions && currentQuestionIndex >= currentQuiz.questions.length" class="text-center py-8">
          <div class="text-6xl mb-4">🎉</div>
          <h3 class="text-2xl font-bold text-purple-900 mb-2">Quiz Complete!</h3>
          <p class="text-lg text-gray-700 mb-6">
            You scored <span class="font-bold text-purple-700">{{ quizScore }}</span> out of {{ currentQuiz.questions.length }}
          </p>
          <button
            @click="finishQuiz"
            class="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-indigo-700 transition-all"
          >
            ▶️ Resume Video
          </button>
        </div>
        
        <!-- Error State -->
        <div v-else class="text-center py-8">
          <div class="text-6xl mb-4">⚠️</div>
          <h3 class="text-2xl font-bold text-red-900 mb-2">Quiz Error</h3>
          <p class="text-lg text-gray-700 mb-6">
            No questions available. Please try again.
          </p>
          <button
            @click="resumeVideo"
            class="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-indigo-700 transition-all"
          >
            ▶️ Resume Video
          </button>
        </div>
        </div>
      </div>

      <!-- Study Progress Panel -->
      <div class="bg-white rounded-xl p-6 shadow-lg">
        <h3 class="text-lg font-semibold text-purple-900 mb-4">📊 Session Progress</h3>
        <div class="grid grid-cols-4 gap-4">
          <div class="text-center p-3 bg-purple-50 rounded-lg">
            <div class="text-2xl font-bold text-purple-700">{{ completedCheckpoints }}</div>
            <div class="text-xs text-gray-600">Quizzes Done</div>
          </div>
          <div class="text-center p-3 bg-green-50 rounded-lg">
            <div class="text-2xl font-bold text-green-700">{{ totalCorrectAnswers }}</div>
            <div class="text-xs text-gray-600">Correct</div>
          </div>
          <div class="text-center p-3 bg-amber-50 rounded-lg">
            <div class="text-2xl font-bold text-amber-700">
              {{ Math.round((totalCorrectAnswers / Math.max(totalAnsweredQuestions, 1)) * 100) }}%
            </div>
            <div class="text-xs text-gray-600">Accuracy</div>
          </div>
          <div class="text-center p-3 bg-indigo-50 rounded-lg">
            <div class="text-2xl font-bold text-indigo-700">{{ studyDuration }}</div>
            <div class="text-xs text-gray-600">Time</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Session Complete -->
    <div v-if="sessionComplete" class="bg-white rounded-xl p-8 shadow-lg text-center">
      <div class="text-8xl mb-6">🎓</div>
      <h2 class="text-3xl font-bold text-purple-900 mb-4">Session Complete!</h2>
      <p class="text-lg text-gray-700 mb-6">
        Congratulations! You've completed the study session.
      </p>
      
      <div class="grid grid-cols-3 gap-6 mb-8 max-w-2xl mx-auto">
        <div class="p-4 bg-purple-50 rounded-lg">
          <div class="text-3xl font-bold text-purple-700">{{ totalCheckpoints }}</div>
          <div class="text-sm text-gray-600">Quizzes Completed</div>
        </div>
        <div class="p-4 bg-green-50 rounded-lg">
          <div class="text-3xl font-bold text-green-700">{{ totalCorrectAnswers }}</div>
          <div class="text-sm text-gray-600">Correct Answers</div>
        </div>
        <div class="p-4 bg-amber-50 rounded-lg">
          <div class="text-3xl font-bold text-amber-700">
            {{ Math.round((totalCorrectAnswers / Math.max(totalAnsweredQuestions, 1)) * 100) }}%
          </div>
          <div class="text-sm text-gray-600">Final Score</div>
        </div>
      </div>

      <button
        @click="resetSession"
        class="px-8 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-indigo-700 transition-all"
      >
        🔄 Start New Session
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { fetch as tauriFetch } from '@tauri-apps/api/http'
import { convertFileSrc } from '@tauri-apps/api/tauri'

// Props from parent
const props = defineProps({
  projects: {
    type: Array,
    default: () => []
  }
})

// State
const selectedProject = ref('')
const checkpointInterval = ref(3)
const difficulty = ref('medium')
const loading = ref(false)

const studySession = ref(null)
const videoPath = ref('')
const videoSrc = computed(() => videoPath.value ? convertFileSrc(videoPath.value) : '')
const videoPlayer = ref(null)

const quizMode = ref(false)
const currentQuiz = ref(null)
const currentQuestionIndex = ref(0)
const selectedAnswer = ref(null)
const answerSubmitted = ref(false)
const answerFeedback = ref(null)
const hintShown = ref(false)

const currentSlide = ref(0)
const currentCheckpoint = ref(0)
const completedCheckpoints = ref(0)

const quizScore = ref(0)
const answeredQuestions = ref(0)
const totalCorrectAnswers = ref(0)
const totalAnsweredQuestions = ref(0)

const sessionComplete = ref(false)
const sessionStartTime = ref(null)
const studyDuration = ref('0m')

// Computed
const currentQuestion = computed(() => {
  if (!currentQuiz.value || currentQuestionIndex.value >= currentQuiz.value.questions.length) {
    return null
  }
  return currentQuiz.value.questions[currentQuestionIndex.value]
})

const totalSlides = computed(() => studySession.value?.total_slides || 0)
const totalCheckpoints = computed(() => studySession.value?.checkpoints?.length || 0)

// Methods
async function startStudySession() {
  if (!selectedProject.value) return
  
  loading.value = true
  try {
    // Get quiz checkpoints
    const checkpointsResp = await tauriFetch(
      `http://127.0.0.1:8765/get_quiz_checkpoints?project=${selectedProject.value}&checkpoint_interval=${checkpointInterval.value}`,
      { method: 'GET', responseType: 1 }
    )
    
    if (!checkpointsResp.ok) {
      alert('Failed to initialize study session')
      return
    }
    
    // Get video path
    const videoResp = await tauriFetch(
      `http://127.0.0.1:8765/get_video?project=${selectedProject.value}`,
      { method: 'GET', responseType: 1 }
    )
    
    if (!videoResp.ok || !videoResp.data.exists) {
      alert('Video not found for this project')
      return
    }
    
    studySession.value = checkpointsResp.data
    videoPath.value = videoResp.data.video_path
    sessionStartTime.value = Date.now()
    
    // Load slide timings for accurate slide tracking
    try {
      const timingsResp = await tauriFetch(
        `http://127.0.0.1:8765/get_slide_timings?project=${selectedProject.value}`,
        { method: 'GET', responseType: 1 }
      )
      if (timingsResp.ok && timingsResp.data.slides) {
        studySession.value.slide_timings = timingsResp.data.slides
        console.log('Loaded slide timings:', studySession.value.slide_timings)
      }
    } catch (error) {
      console.warn('Failed to load slide timings, falling back to approximate calculation:', error)
    }
    
    // Start duration timer
    startDurationTimer()
    
  } catch (error) {
    console.error('Failed to start study session:', error)
    alert('Failed to start study session: ' + error.message)
  } finally {
    loading.value = false
  }
}

function onVideoTimeUpdate() {
  if (!videoPlayer.value || !studySession.value || quizMode.value) return
  
  const currentTime = videoPlayer.value.currentTime
  const totalDuration = videoPlayer.value.duration
  
  if (totalDuration > 0) {
    let newSlide = currentSlide.value
    
    // Use actual slide timings if available (ACCURATE)
    if (studySession.value.slide_timings && studySession.value.slide_timings.length > 0) {
      const timings = studySession.value.slide_timings
      
      // Find which slide the current time falls into
      for (let i = 0; i < timings.length; i++) {
        if (currentTime >= timings[i].start && currentTime < timings[i].end) {
          newSlide = i
          break
        }
      }
      
      // Handle end of video (might be past last slide's end time)
      if (currentTime >= timings[timings.length - 1].end) {
        newSlide = timings.length - 1
      }
    } else {
      // Fallback to linear approximation (INACCURATE but better than nothing)
      console.warn('Using approximate slide calculation - slide timings not loaded')
      const slideProgress = (currentTime / totalDuration) * totalSlides.value
      newSlide = Math.floor(slideProgress)
    }
    
    if (newSlide !== currentSlide.value) {
      currentSlide.value = newSlide
      checkForQuizCheckpoint()
    }
  }
}

function checkForQuizCheckpoint() {
  if (!studySession.value || quizMode.value) return
  
  const checkpoints = studySession.value.checkpoints
  const nextCheckpoint = checkpoints[currentCheckpoint.value]
  
  if (nextCheckpoint !== undefined && currentSlide.value >= nextCheckpoint) {
    pauseForQuiz()
  }
}

async function pauseForQuiz() {
  console.log('=== PAUSE FOR QUIZ START ===')
  console.log('Current checkpoint:', currentCheckpoint.value)
  console.log('Study session:', studySession.value)
  console.log('Video element:', videoPlayer.value)
  
  if (videoPlayer.value) {
    try {
      videoPlayer.value.pause()
      console.log('✓ Video paused successfully')
    } catch (error) {
      console.error('✗ Error pausing video:', error)
    }
  } else {
    console.warn('✗ Video player element not found!')
  }
  
  quizMode.value = true
  loading.value = true
  
  try {
    // Determine slide range for this quiz
    const checkpoints = studySession.value.checkpoints
    const slideEnd = checkpoints[currentCheckpoint.value]
    const slideStart = currentCheckpoint.value === 0 ? 0 : checkpoints[currentCheckpoint.value - 1] + 1
    
    console.log('Quiz parameters:', {
      project: selectedProject.value,
      slide_start: slideStart,
      slide_end: slideEnd,
      num_questions: 5,
      difficulty: difficulty.value
    })
    
    // Generate quiz
    console.log('Sending quiz generation request...')
    const response = await tauriFetch(
      'http://127.0.0.1:8765/generate_quiz',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: {
          type: 'Json',
          payload: {
            project: selectedProject.value,
            slide_start: slideStart,
            slide_end: slideEnd,
            num_questions: 5,
            difficulty: difficulty.value
          }
        },
        responseType: 1
      }
    )
    
    console.log('Quiz response status:', response.status)
    console.log('Quiz response ok:', response.ok)
    console.log('Quiz response data:', response.data)
    
    if (response.ok) {
      const quizData = response.data
      
      // Validate quiz data structure
      if (!quizData || !quizData.questions || !Array.isArray(quizData.questions)) {
        console.error('✗ Invalid quiz data structure:', quizData)
        alert('Quiz data is invalid. Please try again.')
        resumeVideo()
        return
      }
      
      if (quizData.questions.length === 0) {
        console.error('✗ Quiz has no questions!')
        alert('Quiz generation produced no questions. Please try again.')
        resumeVideo()
        return
      }
      
      currentQuiz.value = quizData
      currentQuestionIndex.value = 0
      quizScore.value = 0
      answeredQuestions.value = 0
      console.log('✓ Quiz loaded successfully:', currentQuiz.value)
      console.log('  - Number of questions:', currentQuiz.value.questions.length)
      console.log('  - Questions array:', currentQuiz.value.questions)
      console.log('  - First question:', currentQuiz.value.questions[0])
    } else {
      console.error('✗ Quiz generation failed with status:', response.status)
      alert('Failed to generate quiz: ' + (response.data?.detail || 'Unknown error'))
      resumeVideo()
    }
  } catch (error) {
    console.error('✗ Quiz generation exception:', error)
    console.error('Error stack:', error.stack)
    alert('Failed to generate quiz: ' + error.message)
    resumeVideo()
  } finally {
    loading.value = false
    console.log('=== PAUSE FOR QUIZ END ===')
  }
}

function selectAnswer(option) {
  if (answerSubmitted.value) return
  selectedAnswer.value = option
  submitAnswer()
}

async function submitAnswer() {
  if (!selectedAnswer.value || answerSubmitted.value) return
  
  answerSubmitted.value = true
  
  try {
    const response = await tauriFetch(
      'http://127.0.0.1:8765/submit_quiz_answer',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: {
          type: 'Json',
          payload: {
            project: selectedProject.value,
            checkpoint_id: currentQuiz.value.checkpoint_id,
            question_index: currentQuestionIndex.value,
            user_answer: selectedAnswer.value
          }
        },
        responseType: 1
      }
    )
    
    if (response.ok) {
      answerFeedback.value = response.data
      answeredQuestions.value++
      totalAnsweredQuestions.value++
      
      if (response.data.is_correct) {
        quizScore.value++
        totalCorrectAnswers.value++
      }
    }
  } catch (error) {
    console.error('Failed to submit answer:', error)
    alert('Failed to submit answer')
  }
}

function nextQuestion() {
  currentQuestionIndex.value++
  selectedAnswer.value = null
  answerSubmitted.value = false
  answerFeedback.value = null
  hintShown.value = false
}

function finishQuiz() {
  completedCheckpoints.value++
  currentCheckpoint.value++
  
  quizMode.value = false
  currentQuiz.value = null
  
  if (currentCheckpoint.value >= totalCheckpoints.value) {
    // All quizzes complete
    sessionComplete.value = true
  } else {
    resumeVideo()
  }
}

function resumeVideo() {
  console.log('Resuming video, video element:', videoPlayer.value)
  
  if (videoPlayer.value) {
    try {
      videoPlayer.value.play()
      console.log('Video resumed successfully')
    } catch (error) {
      console.error('Error resuming video:', error)
    }
  } else {
    console.warn('Video player element not found!')
  }
}

function showHint() {
  hintShown.value = true
}

function getOptionClass(option) {
  if (!answerSubmitted.value) {
    return selectedAnswer.value === option
      ? 'border-purple-500 bg-purple-50'
      : 'border-gray-300 hover:border-purple-300 hover:bg-purple-50'
  }
  
  if (answerFeedback.value.correct_answer === option) {
    return 'border-green-500 bg-green-50 text-green-900'
  }
  
  if (selectedAnswer.value === option && !answerFeedback.value.is_correct) {
    return 'border-red-500 bg-red-50 text-red-900'
  }
  
  return 'border-gray-300 opacity-50'
}

function onVideoEnded() {
  if (!quizMode.value && currentCheckpoint.value >= totalCheckpoints.value) {
    sessionComplete.value = true
  }
}

function resetSession() {
  studySession.value = null
  videoPath.value = ''
  quizMode.value = false
  currentQuiz.value = null
  currentSlide.value = 0
  currentCheckpoint.value = 0
  completedCheckpoints.value = 0
  totalCorrectAnswers.value = 0
  totalAnsweredQuestions.value = 0
  sessionComplete.value = false
  selectedProject.value = ''
}

let durationTimer = null

function startDurationTimer() {
  durationTimer = setInterval(() => {
    if (sessionStartTime.value) {
      const elapsed = Math.floor((Date.now() - sessionStartTime.value) / 1000)
      const minutes = Math.floor(elapsed / 60)
      const seconds = elapsed % 60
      studyDuration.value = `${minutes}m ${seconds}s`
    }
  }, 1000)
}

onUnmounted(() => {
  if (durationTimer) {
    clearInterval(durationTimer)
  }
})
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
