<template>
  <div class="lecture-player-container" :class="{ fullscreen: isFullscreen }">
    <!-- Header with Progress Ring -->
    <div class="lecture-header glass-panel">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <!-- Circular Progress Ring -->
          <div class="progress-ring-container">
            <svg class="progress-ring" width="60" height="60">
              <circle
                class="progress-ring-bg"
                cx="30"
                cy="30"
                r="26"
              />
              <circle
                class="progress-ring-fill"
                cx="30"
                cy="30"
                r="26"
                :style="{ strokeDashoffset: progressOffset }"
              />
              <text x="30" y="35" class="progress-text">
                {{ currentSlideNumber }}/{{ totalSlides }}
              </text>
            </svg>
          </div>
          
          <div>
            <h2 class="text-2xl font-bold text-brown-800">🎓 Interactive Lecture</h2>
            <p v-if="currentSlide" class="text-sm text-brown-600 mt-1">
              {{ currentSlide.title || `Slide ${currentSlideNumber}` }}
            </p>
          </div>
        </div>
        
        <div class="flex items-center gap-3">
          <!-- Audio Waveform Indicator -->
          <div v-if="isPlaying" class="waveform-indicator">
            <span class="wave-bar"></span>
            <span class="wave-bar"></span>
            <span class="wave-bar"></span>
            <span class="wave-bar"></span>
          </div>
          
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
    </div>

    <!-- Main Content Area -->
    <div class="lecture-content-wrapper">
      <!-- Slide Content Stage -->
      <div class="slide-stage glass-panel" ref="stageElement">
        <!-- Slide Title - Only show if not already in content items -->
        <transition name="slide-fade" mode="out-in">
          <h1 
            v-if="currentSlide && !isFirstStepTitle" 
            :key="currentSlideNumber" 
            class="slide-title"
          >
            {{ currentSlide.title || `Slide ${currentSlideNumber}` }}
          </h1>
        </transition>

        <!-- Animated Bullet Points / Content -->
        <div class="content-area space-y-4">
          <transition-group name="bullet-list" tag="div" class="space-y-3">
            <div
              v-for="(item, index) in visibleContent"
              :key="`${currentSlideNumber}-${index}`"
              :class="[
                'content-item',
                { 'highlighted-item': index === currentBulletIndex }
              ]"
            >
              <!-- Title (if first item is title type) -->
              <div v-if="item.type === 'title'" class="slide-title-inline">
                {{ item.text }}
              </div>
              
              <!-- Bullet Point -->
              <div v-else-if="item.type === 'bullet'" class="bullet-item">
                <span class="bullet-marker">●</span>
                <span class="bullet-text">{{ item.text }}</span>
              </div>
              
              <!-- Paragraph -->
              <div v-else-if="item.type === 'text'" class="text-item">
                {{ item.text }}
              </div>
              
              <!-- Title/Heading -->
              <div v-else-if="item.type === 'heading'" class="heading-item">
                {{ item.text }}
              </div>
            </div>
          </transition-group>
        </div>

        <!-- Hint Modal/Bubble -->
        <transition name="hint-slide">
          <div v-if="showHintModal" class="hint-modal glass-panel">
            <div class="hint-header">
              <span class="hint-icon">📘</span>
              <h3 class="hint-title">Hint</h3>
              <button @click="closeHint" class="hint-close">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div class="hint-content">
              <div v-if="loadingHint" class="hint-loading">
                <svg class="animate-spin w-6 h-6 text-brown-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <p>Generating hint...</p>
              </div>
              <p v-else class="hint-text">{{ hintText }}</p>
            </div>
          </div>
        </transition>

        <!-- Speaking Pulse Background -->
        <div v-if="isSpeaking" class="speaking-pulse"></div>
      </div>

      <!-- Control Panel -->
      <div class="control-panel glass-panel">
        <h3 class="control-title">Controls</h3>
        
        <!-- Main Control Buttons -->
        <div class="control-grid">
          <!-- Replay Button -->
          <button
            @click="handleReplay"
            class="btn-control btn-replay"
            :disabled="!canInteract || isReplaying"
            title="Replay current segment"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span>Replay</span>
          </button>

          <!-- Next Button -->
          <button
            @click="handleNext"
            class="btn-control btn-next"
            :disabled="!canInteract"
            title="Next bullet point"
          >
            <span>Next</span>
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </button>

          <!-- Hint Button -->
          <button
            @click="handleHint"
            class="btn-control btn-hint"
            :disabled="!canInteract || loadingHint"
            title="Get explanation"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <span>Hint</span>
          </button>
        </div>

        <!-- Play/Pause Large Button -->
        <button
          @click="togglePlayback"
          class="btn-play-large"
          title="Play/Pause lecture"
        >
          <svg v-if="!isPlaying" class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <svg v-else class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </button>

        <!-- Speed Control -->
        <div class="speed-control">
          <label class="speed-label">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <span>Speed</span>
          </label>
          <select
            v-model="playbackSpeed"
            @change="updatePlaybackSpeed"
            class="speed-select"
          >
            <option :value="0.5">0.5×</option>
            <option :value="0.75">0.75×</option>
            <option :value="1">1×</option>
            <option :value="1.25">1.25×</option>
            <option :value="1.5">1.5×</option>
          </select>
        </div>

        <!-- Progress Info -->
        <div class="progress-info">
          <div class="progress-label">Content Progress</div>
          <div class="progress-bar-wrapper">
            <div class="progress-bar-track">
              <div 
                class="progress-bar-fill" 
                :style="{ width: contentProgressPercent + '%' }"
              ></div>
            </div>
            <span class="progress-text-small">
              {{ visibleContent.length }}/{{ totalContentItems }}
            </span>
          </div>
        </div>

        <!-- Debug Info -->
        <div class="debug-info">
          <div class="text-xs text-brown-600">
            <div>Audio: {{ audioElement?.src ? '✅' : '❌' }}</div>
            <div>Playing: {{ isPlaying ? '▶️' : '⏸️' }}</div>
            <div>Time: {{ currentTime.toFixed(1) }}s</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Hidden Audio Element -->
    <audio
      ref="audioElement"
      :src="audioSrc"
      @timeupdate="onAudioTimeUpdate"
      @ended="onAudioEnded"
      @loadedmetadata="onAudioLoaded"
    ></audio>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'

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
  }
})

// State
const audioElement = ref(null)
const stageElement = ref(null)
const isPlaying = ref(false)
const isSpeaking = ref(false)
const isFullscreen = ref(false)
const currentSlideIndex = ref(0)
const currentBulletIndex = ref(0)
const showHintModal = ref(false)
const loadingHint = ref(false)
const hintText = ref('')
const canInteract = ref(false)
const isReplaying = ref(false)
const playbackSpeed = ref(1)
const currentTime = ref(0)
const duration = ref(0)
const visibleContentCount = ref(0)

// Computed
const totalSlides = computed(() => props.animations.slides?.length || 0)

const currentSlideNumber = computed(() => currentSlideIndex.value + 1)

const currentSlide = computed(() => {
  const slide = props.animations.slides?.[currentSlideIndex.value] || null
  if (slide) {
    // If no title property, try to use first step's text or generate one
    if (!slide.title && slide.steps && slide.steps.length > 0) {
      const firstStep = slide.steps[0]
      if (firstStep.element === 'title') {
        slide.title = firstStep.text
      }
    }
    if (!slide.title) {
      slide.title = `Slide ${currentSlideIndex.value + 1}`
    }
  }
  return slide
})

const allContentItems = computed(() => {
  if (!currentSlide.value || !currentSlide.value.steps) return []
  return currentSlide.value.steps.map((step, index) => ({
    type: step.element || 'bullet',
    text: step.text,
    index
  }))
})

const isFirstStepTitle = computed(() => {
  if (allContentItems.value.length === 0) return false
  return allContentItems.value[0].type === 'title'
})

const totalContentItems = computed(() => allContentItems.value.length)

const visibleContent = computed(() => {
  return allContentItems.value.slice(0, visibleContentCount.value)
})

const contentProgressPercent = computed(() => {
  if (totalContentItems.value === 0) return 0
  return (visibleContentCount.value / totalContentItems.value) * 100
})

const progressOffset = computed(() => {
  const circumference = 2 * Math.PI * 26
  const progress = currentSlideNumber.value / totalSlides.value
  return circumference - (progress * circumference)
})

// Methods
function onAudioLoaded() {
  duration.value = audioElement.value?.duration || 0
  console.log('Audio loaded, duration:', duration.value)
}

function onAudioTimeUpdate() {
  if (!audioElement.value) return
  currentTime.value = audioElement.value.currentTime
  
  // Check if speaking (simple audio level simulation)
  isSpeaking.value = isPlaying.value
  
  // Auto-reveal bullets based on timing if not in manual mode
  const currentSlideData = currentSlide.value
  if (currentSlideData && isPlaying.value) {
    // Check if we should reveal next bullet based on timing
    const nextBulletIndex = visibleContentCount.value
    if (nextBulletIndex < totalContentItems.value) {
      const nextStep = currentSlideData.steps?.[nextBulletIndex]
      // Auto-reveal after a delay (simulate narration timing)
      // Each bullet gets roughly equal time in the slide duration
      const slideStart = currentSlideData.start_time || 0
      const slideEnd = currentSlideData.end_time || (slideStart + 10)
      const slideDuration = slideEnd - slideStart
      const timePerStep = slideDuration / totalContentItems.value
      const revealTime = slideStart + (nextBulletIndex * timePerStep)
      
      if (currentTime.value >= revealTime) {
        revealNextBullet()
      }
    }
  }
  
  // Auto-advance slides based on timing
  const nextSlide = props.animations.slides?.[currentSlideIndex.value + 1]
  if (nextSlide && currentTime.value >= nextSlide.start_time) {
    advanceToNextSlide()
  }
}

function onAudioEnded() {
  isPlaying.value = false
  isSpeaking.value = false
  canInteract.value = false
  console.log('Lecture completed!')
}

function togglePlayback() {
  if (!audioElement.value) return
  
  if (isPlaying.value) {
    audioElement.value.pause()
    isPlaying.value = false
    isSpeaking.value = false
  } else {
    audioElement.value.play().catch(err => {
      console.error('Audio playback failed:', err)
      // Try to load and play
      audioElement.value.load()
      setTimeout(() => {
        audioElement.value.play().catch(e => console.error('Retry failed:', e))
      }, 100)
    })
    isPlaying.value = true
    canInteract.value = true
  }
}

function updatePlaybackSpeed() {
  if (audioElement.value) {
    audioElement.value.playbackRate = playbackSpeed.value
  }
}

function advanceToNextSlide() {
  if (currentSlideIndex.value < totalSlides.value - 1) {
    console.log(`Advancing from slide ${currentSlideIndex.value + 1} to ${currentSlideIndex.value + 2}`)
    currentSlideIndex.value++
    visibleContentCount.value = 0
    currentBulletIndex.value = 0
    nextTick(() => {
      revealNextBullet()
    })
  } else {
    console.log('Reached last slide')
  }
}

function revealNextBullet() {
  if (visibleContentCount.value < totalContentItems.value) {
    visibleContentCount.value++
    currentBulletIndex.value = visibleContentCount.value - 1
    console.log(`Revealed bullet ${currentBulletIndex.value + 1}/${totalContentItems.value}`)
  }
}

async function handleNext() {
  if (!canInteract.value) return
  
  if (visibleContentCount.value < totalContentItems.value) {
    revealNextBullet()
  } else {
    advanceToNextSlide()
  }
}

async function handleReplay() {
  if (!audioElement.value || !canInteract.value) return
  
  isReplaying.value = true
  
  try {
    // Just replay from current slide start
    const slide = currentSlide.value
    if (slide && audioElement.value) {
      audioElement.value.currentTime = slide.start_time || 0
      audioElement.value.play()
      isPlaying.value = true
      console.log('Replaying slide from:', slide.start_time)
    }
  } catch (error) {
    console.error('Replay error:', error)
  } finally {
    setTimeout(() => {
      isReplaying.value = false
    }, 500)
  }
}

async function handleHint() {
  if (!canInteract.value || loadingHint.value) return
  
  const currentBullet = visibleContent.value[currentBulletIndex.value]
  if (!currentBullet) return
  
  showHintModal.value = true
  loadingHint.value = true
  hintText.value = ''
  
  try {
    // Try to use the hint from animation data first
    const slide = currentSlide.value
    if (slide && slide.steps && slide.steps[currentBulletIndex.value]) {
      const step = slide.steps[currentBulletIndex.value]
      if (step.hint) {
        hintText.value = step.hint
        loadingHint.value = false
        return
      }
    }
    
    // Generate a simple contextual hint
    hintText.value = `Key point: ${currentBullet.text}\n\nTip: Pay attention to how this concept connects to the overall topic. Try to relate it to examples you already know.`
  } catch (error) {
    console.error('Hint generation error:', error)
    hintText.value = 'This concept relates to the main topic. Try breaking it down into smaller parts to understand better.'
  } finally {
    loadingHint.value = false
  }
}

function closeHint() {
  showHintModal.value = false
}

function toggleFullscreen() {
  isFullscreen.value = !isFullscreen.value
}

// Lifecycle
onMounted(() => {
  console.log('=== LecturePlayer mounted ===')
  console.log('Audio source:', props.audioSrc)
  console.log('Animations:', props.animations)
  console.log('Timings:', props.timings)
  
  // Validate data structure
  if (!props.animations || !props.animations.slides || props.animations.slides.length === 0) {
    console.error('❌ Invalid animations data structure:', props.animations)
    return
  }
  
  console.log(`✅ Found ${props.animations.slides.length} slides`)
  
  // Start with first bullet visible
  nextTick(() => {
    if (currentSlide.value && currentSlide.value.steps && currentSlide.value.steps.length > 0) {
      console.log('✅ First slide:', currentSlide.value)
      console.log(`  - Steps: ${currentSlide.value.steps.length}`)
      revealNextBullet()
    } else {
      console.error('❌ No valid slide data found')
    }
  })
  
  // Ensure audio element is ready
  nextTick(() => {
    if (audioElement.value) {
      console.log('✅ Audio element ready')
      console.log('  - Audio src:', audioElement.value.src)
      
      audioElement.value.addEventListener('error', (e) => {
        console.error('❌ Audio error:', e)
        console.error('  - Audio src:', audioElement.value.src)
        console.error('  - Error code:', audioElement.value.error?.code)
        console.error('  - Error message:', audioElement.value.error?.message)
      })
      
      audioElement.value.addEventListener('loadeddata', () => {
        console.log('✅ Audio loaded successfully')
        console.log('  - Duration:', audioElement.value.duration)
      })
      
      audioElement.value.addEventListener('canplay', () => {
        console.log('✅ Audio can play')
      })
    } else {
      console.error('❌ Audio element not found')
    }
  })
})

onUnmounted(() => {
  if (audioElement.value) {
    audioElement.value.pause()
  }
})
</script>

<style scoped>
/* Container & Layout */
.lecture-player-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-height: calc(100vh - 200px);
  background: linear-gradient(to bottom, #fef3c7, #fde68a);
  padding: 1.5rem;
  border-radius: 1.5rem;
  font-family: 'Nunito', 'Fredoka', sans-serif;
}

.lecture-player-container.fullscreen {
  position: fixed;
  inset: 0;
  z-index: 50;
  max-height: 100vh;
}

.glass-panel {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: 1.5rem;
  box-shadow: 0 8px 32px rgba(139, 115, 85, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.5);
}

/* Header */
.lecture-header {
  padding: 1.25rem 1.5rem;
}

.progress-ring-container {
  position: relative;
}

.progress-ring {
  transform: rotate(-90deg);
}

.progress-ring-bg {
  fill: none;
  stroke: rgba(139, 115, 85, 0.15);
  stroke-width: 4;
}

.progress-ring-fill {
  fill: none;
  stroke: #8b7355;
  stroke-width: 4;
  stroke-dasharray: 163.36;
  transition: stroke-dashoffset 0.3s ease;
}

.progress-text {
  font-size: 0.75rem;
  font-weight: 600;
  fill: #654321;
  text-anchor: middle;
  dominant-baseline: middle;
}

.btn-icon {
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 0.5rem;
  border: none;
  cursor: pointer;
  color: #654321;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: white;
  box-shadow: 0 4px 12px rgba(139, 115, 85, 0.2);
}

/* Waveform Indicator */
.waveform-indicator {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  height: 1.5rem;
}

.wave-bar {
  width: 3px;
  height: 100%;
  background: #8b7355;
  border-radius: 2px;
  animation: wave 1s ease-in-out infinite;
}

.wave-bar:nth-child(1) { animation-delay: 0s; }
.wave-bar:nth-child(2) { animation-delay: 0.2s; }
.wave-bar:nth-child(3) { animation-delay: 0.4s; }
.wave-bar:nth-child(4) { animation-delay: 0.6s; }

@keyframes wave {
  0%, 100% { transform: scaleY(0.3); }
  50% { transform: scaleY(1); }
}

/* Content Wrapper */
.lecture-content-wrapper {
  display: flex;
  gap: 1rem;
  flex: 1;
  overflow: hidden;
}

/* Slide Stage */
.slide-stage {
  flex: 1;
  padding: 2.5rem;
  position: relative;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.slide-title {
  font-size: 2.25rem;
  font-weight: 700;
  color: #654321;
  margin-bottom: 2rem;
  text-align: center;
}

.slide-title-inline {
  font-size: 2rem;
  font-weight: 700;
  color: #654321;
  margin-bottom: 1.5rem;
  text-align: center;
  padding: 1rem;
  background: rgba(222, 184, 135, 0.2);
  border-radius: 1rem;
}

.content-area {
  flex: 1;
}

/* Content Items */
.content-item {
  opacity: 0;
  transform: translateY(20px);
  animation: fadeInUp 0.5s ease forwards;
}

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.bullet-item {
  display: flex;
  align-items: start;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 0.75rem;
  border-left: 4px solid #d2b48c;
  transition: all 0.3s ease;
}

.bullet-item:hover {
  background: rgba(255, 255, 255, 0.9);
  transform: translateX(4px);
}

.highlighted-item .bullet-item {
  background: rgba(255, 237, 213, 0.9);
  border-left-color: #8b7355;
  box-shadow: 0 4px 12px rgba(139, 115, 85, 0.2);
}

.bullet-marker {
  color: #8b7355;
  font-size: 1.25rem;
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.bullet-text {
  color: #654321;
  font-size: 1.125rem;
  line-height: 1.6;
}

.text-item {
  padding: 1rem 1.5rem;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 0.75rem;
  color: #654321;
  font-size: 1.125rem;
  line-height: 1.6;
}

.heading-item {
  font-size: 1.5rem;
  font-weight: 600;
  color: #8b7355;
  margin: 1.5rem 0 0.75rem;
}

/* Transitions */
.slide-fade-enter-active, .slide-fade-leave-active {
  transition: all 0.4s ease;
}

.slide-fade-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.slide-fade-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.bullet-list-enter-active {
  transition: all 0.5s ease;
}

.bullet-list-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

/* Hint Modal */
.hint-modal {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  max-width: 32rem;
  width: 90%;
  z-index: 100;
  overflow: hidden;
}

.hint-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.25rem 1.5rem;
  background: linear-gradient(135deg, #deb887, #d2b48c);
  border-bottom: 1px solid rgba(139, 115, 85, 0.2);
}

.hint-icon {
  font-size: 1.75rem;
}

.hint-title {
  flex: 1;
  font-size: 1.25rem;
  font-weight: 600;
  color: #654321;
}

.hint-close {
  padding: 0.25rem;
  background: rgba(255, 255, 255, 0.5);
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  color: #654321;
  transition: all 0.2s;
}

.hint-close:hover {
  background: white;
}

.hint-content {
  padding: 1.5rem;
}

.hint-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  color: #654321;
}

.hint-text {
  color: #654321;
  font-size: 1rem;
  line-height: 1.6;
}

.hint-slide-enter-active, .hint-slide-leave-active {
  transition: all 0.3s ease;
}

.hint-slide-enter-from, .hint-slide-leave-to {
  opacity: 0;
  transform: translate(-50%, -40%) scale(0.95);
}

/* Speaking Pulse */
.speaking-pulse {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at center, rgba(222, 184, 135, 0.15) 0%, transparent 70%);
  animation: pulse 2s ease-in-out infinite;
  pointer-events: none;
  z-index: 0;
}

@keyframes pulse {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.6; }
}

/* Control Panel */
.control-panel {
  width: 18rem;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.control-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #654321;
  margin-bottom: 0.5rem;
}

.control-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.75rem;
}

.btn-control {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 0.75rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(139, 115, 85, 0.15);
}

.btn-control:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(139, 115, 85, 0.25);
}

.btn-control:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-replay {
  background: linear-gradient(135deg, #60a5fa, #3b82f6);
  color: white;
}

.btn-replay:hover:not(:disabled) {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}

.btn-next {
  background: linear-gradient(135deg, #fb923c, #f97316);
  color: white;
}

.btn-next:hover:not(:disabled) {
  background: linear-gradient(135deg, #f97316, #ea580c);
}

.btn-hint {
  background: linear-gradient(135deg, #ec4899, #db2777);
  color: white;
}

.btn-hint:hover:not(:disabled) {
  background: linear-gradient(135deg, #db2777, #be185d);
}

.btn-play-large {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 4rem;
  height: 4rem;
  margin: 0.75rem auto;
  background: linear-gradient(135deg, #8b7355, #654321);
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(101, 67, 33, 0.3);
  transition: all 0.2s;
}

.btn-play-large:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(101, 67, 33, 0.4);
}

/* Speed Control */
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
  font-weight: 600;
  color: #654321;
}

.speed-select {
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.7);
  color: #654321;
  border: 2px solid #d2b48c;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.speed-select:hover {
  border-color: #8b7355;
  background: white;
}

.speed-select:focus {
  outline: none;
  border-color: #654321;
  box-shadow: 0 0 0 3px rgba(101, 67, 33, 0.1);
}

/* Progress Info */
.progress-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.progress-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #654321;
}

.progress-bar-wrapper {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.progress-bar-track {
  flex: 1;
  height: 0.5rem;
  background: rgba(139, 115, 85, 0.2);
  border-radius: 0.25rem;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #8b7355, #654321);
  transition: width 0.3s ease;
}

.progress-text-small {
  font-size: 0.75rem;
  font-weight: 600;
  color: #8b7355;
}

/* Debug Info */
.debug-info {
  padding: 0.75rem;
  background: rgba(139, 115, 85, 0.1);
  border-radius: 0.5rem;
  margin-top: 0.5rem;
}

.debug-info .text-xs {
  font-size: 0.7rem;
  line-height: 1.4;
}

/* Utility Classes */
.space-y-4 > * + * {
  margin-top: 1rem;
}

.space-y-3 > * + * {
  margin-top: 0.75rem;
}

/* Responsive */
@media (max-width: 1024px) {
  .lecture-content-wrapper {
    flex-direction: column;
  }
  
  .control-panel {
    width: 100%;
  }
  
  .control-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
