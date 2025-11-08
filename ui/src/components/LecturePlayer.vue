<template>
  <div class="lecture-player-container" :class="{ fullscreen: isFullscreen }">
    <!-- Header -->
    <div class="lecture-header glass-card">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-2xl font-bold text-amber-900">🎓 Interactive Lecture</h2>
          <p v-if="currentSlide" class="text-sm text-gray-600 mt-1">
            Slide {{ currentSlide.slide_number }} of {{ totalSlides }}
          </p>
        </div>
        <div class="flex gap-3">
          <button
            @click="toggleFullscreen"
            class="btn-control"
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
      <!-- Animation Stage -->
      <div class="animation-stage glass-card" ref="stageElement">
        <!-- Current Animation Step -->
        <div
          v-for="step in currentAnimationSteps"
          :key="step.id"
          :ref="(el) => setStepRef(el, step.id)"
          :class="['animation-step', `step-${step.element}`]"
          :data-step-id="step.id"
        >
          <div v-if="step.element === 'title'" class="step-title">
            {{ step.text }}
          </div>
          <div v-else-if="step.element === 'bullet'" class="step-bullet">
            <span class="bullet-marker">●</span>
            <span class="bullet-text">{{ step.text }}</span>
          </div>
          <div v-else class="step-text">
            {{ step.text }}
          </div>
        </div>

        <!-- Hint Bubble (appears on demand) -->
        <transition name="hint-fade">
          <div v-if="showHint && currentHint" class="hint-bubble">
            <div class="hint-icon">💡</div>
            <div class="hint-text">{{ currentHint }}</div>
          </div>
        </transition>

        <!-- Progress Bar -->
        <div class="progress-container">
          <div class="progress-bar" :style="{ width: progressPercent + '%' }"></div>
        </div>
      </div>

      <!-- Interactive Controls -->
      <div class="control-panel glass-card">
        <div class="flex items-center justify-center gap-4">
          <!-- Replay Button -->
          <button
            @click="replayStep"
            class="btn-interactive replay"
            :disabled="!canInteract"
            title="Replay current step"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span>Replay</span>
          </button>

          <!-- Play/Pause Audio -->
          <button
            @click="toggleAudio"
            class="btn-interactive play"
            title="Play/Pause narration"
          >
            <svg v-if="!isPlaying" class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <svg v-else class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </button>

          <!-- Next Step Button -->
          <button
            @click="nextStep"
            class="btn-interactive next"
            :disabled="!canInteract"
            title="Next step"
          >
            <span>Next</span>
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
            </svg>
          </button>

          <!-- Hint Button -->
          <button
            @click="toggleHint"
            class="btn-interactive hint"
            :class="{ active: showHint }"
            :disabled="!canInteract"
            title="Show/Hide hint"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <span>Hint</span>
          </button>
        </div>

        <!-- Playback Speed Control -->
        <div class="flex items-center justify-center gap-2 mt-3">
          <label class="text-sm text-gray-600">Speed:</label>
          <select
            v-model="playbackSpeed"
            @change="updatePlaybackSpeed"
            class="px-2 py-1 border rounded text-sm"
          >
            <option :value="0.5">0.5x</option>
            <option :value="0.75">0.75x</option>
            <option :value="1">1x</option>
            <option :value="1.25">1.25x</option>
            <option :value="1.5">1.5x</option>
          </select>
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
import gsap from 'gsap'

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
const isFullscreen = ref(false)
const currentSlideIndex = ref(0)
const currentStepIndex = ref(0)
const showHint = ref(false)
const canInteract = ref(false)
const playbackSpeed = ref(1)
const currentTime = ref(0)
const duration = ref(0)
const stepRefs = ref({})

// Computed
const totalSlides = computed(() => props.animations.slides?.length || 0)

const currentSlide = computed(() => {
  return props.animations.slides?.[currentSlideIndex.value] || null
})

const currentAnimationSteps = computed(() => {
  if (!currentSlide.value) return []
  return currentSlide.value.steps.slice(0, currentStepIndex.value + 1)
})

const currentHint = computed(() => {
  const slide = currentSlide.value
  if (!slide || !slide.steps) return ''
  const step = slide.steps[currentStepIndex.value]
  return step?.hint || ''
})

const progressPercent = computed(() => {
  if (!duration.value) return 0
  return (currentTime.value / duration.value) * 100
})

// Methods
function setStepRef(el, stepId) {
  if (el) {
    stepRefs.value[stepId] = el
  }
}

function onAudioLoaded() {
  duration.value = audioElement.value.duration
  console.log('Audio loaded, duration:', duration.value)
}

function onAudioTimeUpdate() {
  if (!audioElement.value) return
  currentTime.value = audioElement.value.currentTime
  
  // Check if we should advance to next slide based on timing
  const nextSlide = props.animations.slides?.[currentSlideIndex.value + 1]
  if (nextSlide && currentTime.value >= nextSlide.start_time) {
    advanceToNextSlide()
  }
}

function onAudioEnded() {
  isPlaying.value = false
  canInteract.value = false
  console.log('Lecture completed!')
}

function toggleAudio() {
  if (!audioElement.value) return
  
  if (isPlaying.value) {
    audioElement.value.pause()
    isPlaying.value = false
  } else {
    audioElement.value.play()
    isPlaying.value = true
    canInteract.value = true
  }
}

function updatePlaybackSpeed() {
  if (audioElement.value) {
    audioElement.value.playbackRate = playbackSpeed.value
  }
}

async function advanceToNextSlide() {
  currentSlideIndex.value++
  currentStepIndex.value = 0
  showHint.value = false
  
  // Clear stage
  if (stageElement.value) {
    gsap.to(stageElement.value.children, {
      opacity: 0,
      duration: 0.3,
      onComplete: () => {
        nextTick(() => animateStep(0))
      }
    })
  }
}

async function nextStep() {
  const slide = currentSlide.value
  if (!slide || !slide.steps) return
  
  if (currentStepIndex.value < slide.steps.length - 1) {
    currentStepIndex.value++
    await nextTick()
    animateStep(currentStepIndex.value)
  } else {
    // All steps shown, move to next slide
    advanceToNextSlide()
  }
}

function animateStep(stepIndex) {
  const slide = currentSlide.value
  if (!slide || !slide.steps) return
  
  const step = slide.steps[stepIndex]
  if (!step) return
  
  const element = stepRefs.value[step.id]
  if (!element) return
  
  // Reset element
  gsap.set(element, { opacity: 0, x: 0, y: 0, scale: 1 })
  
  // Apply animation based on action type
  switch (step.action) {
    case 'fadeIn':
      gsap.to(element, {
        opacity: 1,
        duration: step.duration || 1.5,
        ease: 'power2.out'
      })
      break
    
    case 'slideIn':
      gsap.fromTo(element,
        { opacity: 0, x: -50 },
        {
          opacity: 1,
          x: 0,
          duration: step.duration || 1.5,
          ease: 'back.out'
        }
      )
      break
    
    case 'highlight':
      gsap.fromTo(element,
        { opacity: 0, backgroundColor: '#fff' },
        {
          opacity: 1,
          backgroundColor: '#fef3c7',
          duration: step.duration || 1,
          ease: 'power2.out',
          yoyo: true,
          repeat: 1
        }
      )
      break
    
    case 'pulse':
      gsap.fromTo(element,
        { opacity: 0, scale: 0.8 },
        {
          opacity: 1,
          scale: 1,
          duration: step.duration || 1,
          ease: 'elastic.out',
          repeat: 2,
          yoyo: true
        }
      )
      break
    
    case 'zoom':
      gsap.fromTo(element,
        { opacity: 0, scale: 0.5 },
        {
          opacity: 1,
          scale: 1,
          duration: step.duration || 1.5,
          ease: 'back.out'
        }
      )
      break
    
    case 'typewriter':
      // Typewriter effect would need different implementation
      gsap.to(element, {
        opacity: 1,
        duration: step.duration || 2,
        ease: 'none'
      })
      break
    
    default:
      gsap.to(element, {
        opacity: 1,
        duration: step.duration || 1.5
      })
  }
}

function replayStep() {
  animateStep(currentStepIndex.value)
}

function toggleHint() {
  showHint.value = !showHint.value
  
  if (showHint.value) {
    // Auto-hide after 5 seconds
    setTimeout(() => {
      showHint.value = false
    }, 5000)
  }
}

function toggleFullscreen() {
  isFullscreen.value = !isFullscreen.value
}

// Lifecycle
onMounted(() => {
  console.log('LecturePlayer mounted')
  console.log('Animations:', props.animations)
  console.log('Timings:', props.timings)
  
  // Start with first slide, first step
  nextTick(() => {
    if (currentSlide.value) {
      animateStep(0)
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
.lecture-player-container {
  @apply w-full flex flex-col gap-4 bg-gradient-to-br from-amber-50 to-orange-50;
  max-height: calc(100vh - 200px);
}

.lecture-player-container.fullscreen {
  @apply fixed inset-0 z-50;
  max-height: 100vh;
}

.glass-card {
  @apply bg-white/80 backdrop-blur-xl rounded-2xl shadow-lg border border-white/50;
}

.lecture-header {
  @apply p-4;
}

.lecture-content-wrapper {
  @apply flex gap-4;
  height: 600px;
}

.animation-stage {
  @apply flex-1 p-8 relative;
  @apply flex flex-col items-center justify-center;
  overflow-y: auto;
}

.animation-step {
  @apply opacity-0 mb-4 w-full max-w-3xl;
}

.step-title {
  @apply text-3xl font-bold text-amber-900 text-center mb-4;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}

.step-bullet {
  @apply flex items-start gap-3 text-lg text-gray-800 p-3 rounded-lg bg-white/60;
}

.bullet-marker {
  @apply text-amber-500 text-xl flex-shrink-0;
}

.bullet-text {
  @apply flex-1;
}

.step-text {
  @apply text-xl text-gray-800 p-4 rounded-lg bg-white/60;
}

.hint-bubble {
  @apply absolute bottom-20 left-1/2 transform -translate-x-1/2;
  @apply bg-gradient-to-r from-purple-500 to-pink-500;
  @apply text-white px-6 py-3 rounded-xl shadow-xl;
  @apply flex items-center gap-2 max-w-xl;
  animation: bounce 0.5s ease-in-out;
  z-index: 10;
}

.hint-icon {
  @apply text-2xl;
}

.hint-text {
  @apply text-sm font-medium;
}

@keyframes bounce {
  0%, 100% { transform: translateX(-50%) translateY(0); }
  50% { transform: translateX(-50%) translateY(-10px); }
}

.hint-fade-enter-active, .hint-fade-leave-active {
  transition: all 0.3s ease;
}

.hint-fade-enter-from, .hint-fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(20px);
}

.progress-container {
  @apply absolute bottom-0 left-0 right-0 h-2 bg-gray-200/50;
}

.progress-bar {
  @apply h-full bg-gradient-to-r from-amber-400 to-orange-500;
  transition: width 0.1s linear;
}

.control-panel {
  @apply w-64 p-4 flex flex-col items-center justify-center gap-3;
}

.btn-control {
  @apply p-2 bg-white/80 hover:bg-white rounded-full;
  @apply transition-all shadow-md hover:shadow-lg;
  @apply text-gray-700 hover:text-amber-600;
}

.btn-interactive {
  @apply px-4 py-2 rounded-lg font-semibold text-sm;
  @apply flex items-center gap-2;
  @apply transition-all transform hover:scale-105;
  @apply shadow-md hover:shadow-lg;
  @apply disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none;
}

.btn-interactive.replay {
  @apply bg-gradient-to-r from-blue-500 to-blue-600 text-white;
  @apply hover:from-blue-600 hover:to-blue-700;
}

.btn-interactive.play {
  @apply bg-gradient-to-r from-green-500 to-green-600 text-white;
  @apply hover:from-green-600 hover:to-green-700;
  @apply w-16 h-16 rounded-full justify-center p-0;
}

.btn-interactive.next {
  @apply bg-gradient-to-r from-amber-500 to-orange-500 text-white;
  @apply hover:from-amber-600 hover:to-orange-600;
}

.btn-interactive.hint {
  @apply bg-gradient-to-r from-purple-500 to-pink-500 text-white;
  @apply hover:from-purple-600 hover:to-pink-600;
}

.btn-interactive.hint.active {
  @apply from-pink-600 to-purple-600;
  @apply animate-pulse;
}
</style>
