<template>
  <div class="interactive-lecture-container" :class="{ fullscreen: isFullscreen }">
    <!-- Top Bar -->
    <div class="top-bar glass-panel">
      <div class="lecture-info">
        <h2 class="lecture-title">
          <span class="title-icon">🎓</span>
          <span>Interactive Lecture</span>
        </h2>
        <p class="lecture-subtitle">{{ currentSlide?.title || `Slide ${currentSlideIndex + 1}` }}</p>
      </div>
      
      <div class="top-controls">
        <!-- AI Assistant Trigger -->
        <button
          @click="toggleAssistant"
          class="btn-assistant"
          :class="{ active: showAssistant }"
          title="Ask AI Assistant"
        >
          <span>🤖</span>
          <span>Ask AI</span>
        </button>

        <!-- Fullscreen Toggle -->
        <button
          @click="toggleFullscreen"
          class="btn-icon"
          title="Toggle Fullscreen"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="main-content">
      <!-- Left Sidebar - Progress & Controls -->
      <aside class="sidebar-left glass-panel">
        <ProgressTracker
          :currentSlide="currentSlideIndex + 1"
          :totalSlides="totalSlides"
          :interactionCount="interactionCount"
          :hintsUsed="hintsUsed"
          :slidesViewed="slidesViewed"
          @badgeEarned="handleBadgeEarned"
        />
        
        <!-- Playback Controls -->
        <div class="playback-controls">
          <h4 class="controls-title">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
            <span>Playback</span>
          </h4>
          
          <!-- Play/Pause -->
          <button
            @click="togglePlayback"
            class="btn-play-main"
          >
            <svg v-if="!isPlaying" class="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z" />
            </svg>
            <svg v-else class="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
              <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
            </svg>
            <span>{{ isPlaying ? 'Pause' : 'Play' }}</span>
          </button>

          <!-- Step Controls -->
          <div class="step-controls">
            <button @click="previousStep" class="btn-step" :disabled="currentStepIndex <= 0">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
              <span>Previous</span>
            </button>
            
            <button @click="nextStep" class="btn-step">
              <span>Next</span>
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>

          <!-- Speed Control -->
          <div class="speed-control">
            <label class="speed-label">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <span>Speed: {{ playbackSpeed }}×</span>
            </label>
            <input
              type="range"
              v-model="playbackSpeed"
              min="0.5"
              max="2"
              step="0.25"
              @change="updatePlaybackSpeed"
              class="speed-slider"
            />
          </div>
        </div>
      </aside>

      <!-- Center Stage - Slide Content -->
      <main class="content-stage glass-panel">
        <SlideContent
          ref="slideContentRef"
          :slide="currentSlide"
          :slideIndex="currentSlideIndex"
          :projectName="projectName"
          :autoPlay="isPlaying"
          :currentStep="currentStepIndex"
          :highlightedIndex="highlightedStepIndex"
          @stepComplete="handleStepComplete"
          @interactionUpdate="handleInteraction"
        />

        <!-- Audio Element -->
        <audio
          ref="audioElement"
          :src="audioSrc"
          @timeupdate="onAudioTimeUpdate"
          @ended="onAudioEnded"
          @loadedmetadata="onAudioLoaded"
        ></audio>
      </main>

      <!-- Right Sidebar - Navigation & Hints -->
      <aside class="sidebar-right glass-panel">
        <!-- Slide Navigation -->
        <div class="slide-navigation">
          <h4 class="nav-title">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span>Slides</span>
          </h4>
          
          <div class="slides-list">
            <button
              v-for="(slide, index) in allSlides"
              :key="index"
              @click="goToSlide(index)"
              class="slide-item"
              :class="{ active: index === currentSlideIndex, viewed: viewedSlides.has(index) }"
            >
              <span class="slide-number">{{ index + 1 }}</span>
              <span class="slide-title-mini">{{ slide.title || `Slide ${index + 1}` }}</span>
              <span v-if="viewedSlides.has(index)" class="slide-check">✓</span>
            </button>
          </div>
        </div>

        <!-- Quick Hint Button -->
        <button
          @click="showHint"
          class="btn-hint-quick"
          :disabled="!canShowHint"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          <span>Get Hint</span>
        </button>
      </aside>
    </div>

    <!-- AI Assistant Panel -->
    <AssistantPanel
      :isOpen="showAssistant"
      :currentSlide="currentSlide"
      :currentContent="currentSlideContent"
      @close="closeAssistant"
    />

    <!-- Hint Modal -->
    <Transition name="modal-fade">
      <div v-if="showHintModal" class="hint-overlay" @click.self="closeHint">
        <div class="hint-modal glass-panel">
          <div class="hint-header">
            <span class="hint-icon">💡</span>
            <h3>Hint</h3>
            <button @click="closeHint" class="close-btn">✕</button>
          </div>
          <div class="hint-body">
            <div v-if="loadingHint" class="hint-loading">
              <svg class="animate-spin w-8 h-8" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <p>Generating hint...</p>
            </div>
            <div v-else class="hint-content">
              <p>{{ hintText }}</p>
            </div>
          </div>
          <div class="hint-footer">
            <button @click="closeHint" class="btn-hint-ok">Got it!</button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import SlideContent from './SlideContent.vue'
import AssistantPanel from './AssistantPanel.vue'
import ProgressTracker from './ProgressTracker.vue'

// Props
const props = defineProps({
  audioSrc: {
    type: String,
    required: true
  },
  timings: {
    type: Object,
    required: true
  },
  animations: {
    type: Object,
    required: true
  },
  projectName: {
    type: String,
    required: true
  }
})

// Refs
const slideContentRef = ref(null)
const audioElement = ref(null)

// State
const isPlaying = ref(false)
const isFullscreen = ref(false)
const currentSlideIndex = ref(0)
const currentStepIndex = ref(0)
const highlightedStepIndex = ref(-1)
const playbackSpeed = ref(1)
const currentTime = ref(0)
const duration = ref(0)
const showAssistant = ref(false)
const showHintModal = ref(false)
const loadingHint = ref(false)
const hintText = ref('')
const interactionCount = ref(0)
const hintsUsed = ref(0)
const slidesViewed = ref(0)
const viewedSlides = ref(new Set())

// Computed
const allSlides = computed(() => props.animations.slides || [])
const totalSlides = computed(() => allSlides.value.length)
const currentSlide = computed(() => allSlides.value[currentSlideIndex.value] || null)
const canShowHint = computed(() => currentSlide.value && currentSlide.value.steps && currentSlide.value.steps.length > 0)

const currentSlideContent = computed(() => {
  if (!currentSlide.value || !currentSlide.value.steps) return ''
  return currentSlide.value.steps.map(step => step.text).join(' ')
})

// Methods
function togglePlayback() {
  if (!audioElement.value) return
  
  if (isPlaying.value) {
    audioElement.value.pause()
    isPlaying.value = false
  } else {
    audioElement.value.play().catch(err => {
      console.error('Audio playback failed:', err)
    })
    isPlaying.value = true
    
    // Trigger slide animation when playing
    nextTick(() => {
      if (slideContentRef.value) {
        slideContentRef.value.playAllSteps()
      }
    })
  }
}

function updatePlaybackSpeed() {
  if (audioElement.value) {
    audioElement.value.playbackRate = playbackSpeed.value
  }
}

function toggleAssistant() {
  showAssistant.value = !showAssistant.value
}

function closeAssistant() {
  showAssistant.value = false
}

function toggleFullscreen() {
  isFullscreen.value = !isFullscreen.value
}

function nextStep() {
  if (!currentSlide.value) return
  
  const totalSteps = currentSlide.value.steps?.length || 0
  
  if (currentStepIndex.value < totalSteps - 1) {
    currentStepIndex.value++
    highlightedStepIndex.value = currentStepIndex.value
    if (slideContentRef.value) {
      slideContentRef.value.playStep(currentStepIndex.value)
    }
  } else {
    // Move to next slide
    if (currentSlideIndex.value < totalSlides.value - 1) {
      goToSlide(currentSlideIndex.value + 1)
    }
  }
  
  interactionCount.value++
}

function previousStep() {
  if (currentStepIndex.value > 0) {
    currentStepIndex.value--
    highlightedStepIndex.value = currentStepIndex.value
    if (slideContentRef.value) {
      slideContentRef.value.playStep(currentStepIndex.value)
    }
    interactionCount.value++
  } else if (currentSlideIndex.value > 0) {
    goToSlide(currentSlideIndex.value - 1)
  }
}

function goToSlide(index) {
  if (index < 0 || index >= totalSlides.value) return
  
  currentSlideIndex.value = index
  currentStepIndex.value = 0
  highlightedStepIndex.value = 0
  
  // Mark as viewed
  if (!viewedSlides.value.has(index)) {
    viewedSlides.value.add(index)
    slidesViewed.value = viewedSlides.value.size
  }
  
  // Seek audio to slide start
  const slide = currentSlide.value
  if (slide && audioElement.value) {
    audioElement.value.currentTime = slide.start_time || 0
  }
  
  // Reset animation
  nextTick(() => {
    if (slideContentRef.value) {
      slideContentRef.value.resetAnimation()
      if (isPlaying.value) {
        slideContentRef.value.playAllSteps()
      }
    }
  })
  
  interactionCount.value++
}

async function showHint() {
  if (!canShowHint.value) return
  
  showHintModal.value = true
  loadingHint.value = true
  hintText.value = ''
  hintsUsed.value++
  
  try {
    const step = currentSlide.value.steps[currentStepIndex.value]
    
    // Use provided hint if available
    if (step && step.hint) {
      hintText.value = step.hint
    } else {
      // Generate contextual hint
      hintText.value = `💡 Focus on: ${step.text}\n\n✨ Think about how this concept relates to the main topic. Consider breaking it down into smaller parts to understand better.`
    }
  } catch (error) {
    console.error('Hint generation error:', error)
    hintText.value = 'Try to connect this concept to real-world examples you know.'
  } finally {
    loadingHint.value = false
  }
}

function closeHint() {
  showHintModal.value = false
}

function handleStepComplete(stepIndex) {
  console.log(`Step ${stepIndex} completed`)
}

function handleInteraction(data) {
  interactionCount.value++
  console.log('Interaction:', data)
}

function handleBadgeEarned(badges) {
  console.log('Badges earned:', badges)
}

function onAudioLoaded() {
  duration.value = audioElement.value?.duration || 0
}

function onAudioTimeUpdate() {
  if (!audioElement.value) return
  currentTime.value = audioElement.value.currentTime
  
  // Check if we should advance to next step based on audio timing
  if (currentSlide.value && currentSlide.value.steps && isPlaying.value) {
    const steps = currentSlide.value.steps
    const slideStartTime = currentSlide.value.start_time || 0
    const relativeTime = currentTime.value - slideStartTime
    
    // Find which step should be showing based on timing
    for (let i = 0; i < steps.length; i++) {
      const step = steps[i]
      if (step.start_time !== undefined && relativeTime >= step.start_time && i > currentStepIndex.value) {
        currentStepIndex.value = i
        highlightedStepIndex.value = i
        if (slideContentRef.value) {
          slideContentRef.value.playStep(i)
        }
        break
      }
    }
  }
  
  // Auto-advance slides based on timing
  const nextSlide = allSlides.value[currentSlideIndex.value + 1]
  if (nextSlide && currentTime.value >= nextSlide.start_time) {
    goToSlide(currentSlideIndex.value + 1)
  }
}

function onAudioEnded() {
  isPlaying.value = false
}

// Lifecycle
onMounted(() => {
  // Mark first slide as viewed
  viewedSlides.value.add(0)
  slidesViewed.value = 1
  
  // Auto-play first animation
  nextTick(() => {
    if (slideContentRef.value && currentSlide.value) {
      slideContentRef.value.playAllSteps()
    }
  })
})
</script>

<style scoped>
/* Container */
.interactive-lecture-container {
  width: 100%;
  min-height: calc(100vh - 200px);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.5rem;
  background: linear-gradient(to bottom, #fef3c7, #fde68a);
  border-radius: 1.5rem;
  font-family: 'Nunito', 'Fredoka', sans-serif;
}

.interactive-lecture-container.fullscreen {
  position: fixed;
  inset: 0;
  z-index: 1000;
  border-radius: 0;
  min-height: 100vh;
}

.glass-panel {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: 1rem;
  box-shadow: 0 4px 16px rgba(139, 115, 85, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.5);
}

/* Top Bar */
.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
}

.lecture-info {
  flex: 1;
}

.lecture-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.75rem;
  font-weight: 700;
  color: #654321;
  margin: 0;
}

.title-icon {
  font-size: 2rem;
}

.lecture-subtitle {
  margin: 0.5rem 0 0 0;
  font-size: 1rem;
  color: #8b7355;
  font-weight: 500;
}

.top-controls {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.btn-assistant {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: linear-gradient(135deg, #d2b48c, #daa520);
  border: none;
  border-radius: 0.75rem;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(139, 115, 85, 0.2);
}

.btn-assistant:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(139, 115, 85, 0.3);
}

.btn-assistant.active {
  background: linear-gradient(135deg, #8b7355, #654321);
}

.btn-icon {
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.8);
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  color: #654321;
  transition: all 0.2s ease;
}

.btn-icon:hover {
  background: white;
  box-shadow: 0 2px 8px rgba(139, 115, 85, 0.2);
}

/* Main Content */
.main-content {
  display: grid;
  grid-template-columns: 300px 1fr 250px;
  gap: 1rem;
  flex: 1;
  overflow: hidden;
}

/* Sidebar Left */
.sidebar-left {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1.5rem;
  overflow-y: auto;
}

.playback-controls {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.controls-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.95rem;
  font-weight: 600;
  color: #654321;
  margin: 0 0 0.5rem 0;
}

.btn-play-main {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #8b7355, #654321);
  border: none;
  border-radius: 1rem;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(139, 115, 85, 0.3);
}

.btn-play-main:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 20px rgba(139, 115, 85, 0.4);
}

.step-controls {
  display: flex;
  gap: 0.5rem;
}

.btn-step {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: white;
  border: 2px solid #d2b48c;
  border-radius: 0.5rem;
  color: #654321;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-step:hover:not(:disabled) {
  background: rgba(210, 180, 140, 0.2);
  border-color: #8b7355;
}

.btn-step:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.speed-control {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.speed-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #654321;
}

.speed-slider {
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: linear-gradient(to right, #d2b48c, #daa520);
  outline: none;
  -webkit-appearance: none;
  appearance: none;
}

.speed-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: white;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  border: 2px solid #8b7355;
}

/* Content Stage */
.content-stage {
  padding: 2rem;
  overflow-y: auto;
  position: relative;
}

/* Sidebar Right */
.sidebar-right {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1.5rem;
  overflow-y: auto;
}

.slide-navigation {
  flex: 1;
}

.nav-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.95rem;
  font-weight: 600;
  color: #654321;
  margin: 0 0 1rem 0;
}

.slides-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.slide-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: white;
  border: 2px solid transparent;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

.slide-item:hover {
  background: rgba(210, 180, 140, 0.1);
  border-color: #d2b48c;
}

.slide-item.active {
  background: linear-gradient(135deg, rgba(210, 180, 140, 0.3), rgba(218, 165, 32, 0.3));
  border-color: #daa520;
}

.slide-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  background: #d2b48c;
  color: white;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 0.875rem;
  flex-shrink: 0;
}

.slide-item.active .slide-number {
  background: #daa520;
}

.slide-title-mini {
  flex: 1;
  font-size: 0.875rem;
  color: #654321;
  font-weight: 500;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
}

.slide-check {
  color: #10b981;
  font-size: 1.25rem;
  flex-shrink: 0;
}

.btn-hint-quick {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem;
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  border: none;
  border-radius: 0.75rem;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(251, 191, 36, 0.3);
}

.btn-hint-quick:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(251, 191, 36, 0.4);
}

.btn-hint-quick:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* Hint Modal */
.hint-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.hint-modal {
  max-width: 500px;
  width: 100%;
  overflow: hidden;
}

.hint-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  color: white;
}

.hint-icon {
  font-size: 2rem;
}

.hint-header h3 {
  flex: 1;
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
}

.close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 0.5rem;
  padding: 0.5rem;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
  font-size: 1.25rem;
  transition: background 0.2s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.hint-body {
  padding: 2rem;
  background: white;
  min-height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hint-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  color: #8b7355;
}

.hint-content p {
  margin: 0;
  color: #654321;
  line-height: 1.7;
  font-size: 1.05rem;
  white-space: pre-line;
}

.hint-footer {
  padding: 1.5rem;
  background: white;
  border-top: 2px solid rgba(139, 115, 85, 0.2);
}

.btn-hint-ok {
  width: 100%;
  padding: 0.75rem;
  background: linear-gradient(135deg, #d2b48c, #daa520);
  border: none;
  border-radius: 0.5rem;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-hint-ok:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(139, 115, 85, 0.3);
}

/* Transitions */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: all 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-from .hint-modal,
.modal-fade-leave-to .hint-modal {
  transform: scale(0.9) translateY(-20px);
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(210, 180, 140, 0.2);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #d2b48c;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #8b7355;
}
</style>
