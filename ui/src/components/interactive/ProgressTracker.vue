<template>
  <div class="progress-tracker">
    <!-- Progress Bar -->
    <div class="progress-bar-section">
      <div class="progress-header">
        <span class="progress-label">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
          Lecture Progress
        </span>
        <span class="progress-percent">{{ progressPercent }}%</span>
      </div>
      <div class="progress-bar-track">
        <div 
          class="progress-bar-fill" 
          :style="{ width: progressPercent + '%' }"
        >
          <div class="progress-glow"></div>
        </div>
      </div>
      <div class="progress-details">
        <span>Slide {{ currentSlide }}/{{ totalSlides }}</span>
        <span>•</span>
        <span>{{ interactionCount }} interactions</span>
      </div>
    </div>

    <!-- Badges Section -->
    <div class="badges-section">
      <h4 class="badges-title">
        <span>🏆</span>
        <span>Achievements</span>
      </h4>
      <div class="badges-grid">
        <div
          v-for="badge in allBadges"
          :key="badge.id"
          class="badge-card"
          :class="{ earned: badge.earned, locked: !badge.earned }"
          :title="badge.description"
        >
          <div class="badge-icon">{{ badge.icon }}</div>
          <div class="badge-name">{{ badge.name }}</div>
          <div v-if="badge.earned" class="badge-earned-indicator">✓</div>
        </div>
      </div>
    </div>

    <!-- Stats Section -->
    <div class="stats-section">
      <div class="stat-item">
        <div class="stat-icon">👀</div>
        <div class="stat-content">
          <div class="stat-value">{{ slidesViewed }}</div>
          <div class="stat-label">Slides Viewed</div>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon">💡</div>
        <div class="stat-content">
          <div class="stat-value">{{ hintsUsed }}</div>
          <div class="stat-label">Hints Used</div>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon">🎯</div>
        <div class="stat-content">
          <div class="stat-value">{{ interactionCount }}</div>
          <div class="stat-label">Interactions Made</div>
        </div>
      </div>
    </div>

    <!-- Motivational Message -->
    <transition name="message-fade">
      <div v-if="showMotivation" class="motivation-message">
        <div class="motivation-icon">{{ motivationData.icon }}</div>
        <div class="motivation-text">{{ motivationData.message }}</div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  currentSlide: {
    type: Number,
    required: true
  },
  totalSlides: {
    type: Number,
    required: true
  },
  interactionCount: {
    type: Number,
    default: 0
  },
  hintsUsed: {
    type: Number,
    default: 0
  },
  slidesViewed: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['badgeEarned'])

// State
const showMotivation = ref(false)
const motivationData = ref({ icon: '', message: '' })
const earnedBadges = ref(new Set())

// Load progress from localStorage
const storageKey = 'lectra-progress'
const loadProgress = () => {
  try {
    const saved = localStorage.getItem(storageKey)
    if (saved) {
      const data = JSON.parse(saved)
      earnedBadges.value = new Set(data.badges || [])
    }
  } catch (e) {
    console.error('Failed to load progress:', e)
  }
}

const saveProgress = () => {
  try {
    const data = {
      badges: Array.from(earnedBadges.value),
      lastUpdated: new Date().toISOString()
    }
    localStorage.setItem(storageKey, JSON.stringify(data))
  } catch (e) {
    console.error('Failed to save progress:', e)
  }
}

// Computed
const progressPercent = computed(() => {
  if (props.totalSlides === 0) return 0
  return Math.round((props.currentSlide / props.totalSlides) * 100)
})

const allBadges = computed(() => {
  return [
    {
      id: 'first-slide',
      name: 'First Steps',
      icon: '🎯',
      description: 'Viewed your first slide',
      earned: earnedBadges.value.has('first-slide')
    },
    {
      id: 'halfway',
      name: 'Halfway There',
      icon: '⚡',
      description: 'Completed 50% of the lecture',
      earned: earnedBadges.value.has('halfway')
    },
    {
      id: 'complete',
      name: 'Lecture Master',
      icon: '🎓',
      description: 'Completed the entire lecture',
      earned: earnedBadges.value.has('complete')
    },
    {
      id: 'curious',
      name: 'Curious Mind',
      icon: '🔍',
      description: 'Used hints 5 times',
      earned: earnedBadges.value.has('curious')
    },
    {
      id: 'interactive',
      name: 'Interactive Learner',
      icon: '🎮',
      description: 'Made 10 interactions',
      earned: earnedBadges.value.has('interactive')
    },
    {
      id: 'explorer',
      name: 'Knowledge Explorer',
      icon: '🗺️',
      description: 'Viewed all slides',
      earned: earnedBadges.value.has('explorer')
    }
  ]
})

// Methods
function checkBadges() {
  const newBadges = []

  // First slide
  if (props.slidesViewed >= 1 && !earnedBadges.value.has('first-slide')) {
    earnBadge('first-slide', '🎯', 'First steps taken!')
    newBadges.push('first-slide')
  }

  // Halfway
  if (progressPercent.value >= 50 && !earnedBadges.value.has('halfway')) {
    earnBadge('halfway', '⚡', "You're halfway there!")
    newBadges.push('halfway')
  }

  // Complete
  if (progressPercent.value >= 100 && !earnedBadges.value.has('complete')) {
    earnBadge('complete', '🎓', 'Lecture completed! Amazing work!')
    newBadges.push('complete')
  }

  // Curious
  if (props.hintsUsed >= 5 && !earnedBadges.value.has('curious')) {
    earnBadge('curious', '🔍', 'Curious mind unlocked!')
    newBadges.push('curious')
  }

  // Interactive
  if (props.interactionCount >= 10 && !earnedBadges.value.has('interactive')) {
    earnBadge('interactive', '🎮', 'Interactive learner badge earned!')
    newBadges.push('interactive')
  }

  // Explorer
  if (props.slidesViewed >= props.totalSlides && !earnedBadges.value.has('explorer')) {
    earnBadge('explorer', '🗺️', 'All slides explored!')
    newBadges.push('explorer')
  }

  if (newBadges.length > 0) {
    saveProgress()
    emit('badgeEarned', newBadges)
  }
}

function earnBadge(badgeId, icon, message) {
  earnedBadges.value.add(badgeId)
  showMotivationalMessage(icon, message)
}

function showMotivationalMessage(icon, message) {
  motivationData.value = { icon, message }
  showMotivation.value = true

  setTimeout(() => {
    showMotivation.value = false
  }, 4000)
}

// Watchers
watch([
  () => props.currentSlide,
  () => props.interactionCount,
  () => props.hintsUsed,
  () => props.slidesViewed
], () => {
  checkBadges()
})

// Lifecycle
loadProgress()
checkBadges()
</script>

<style scoped>
.progress-tracker {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(16px);
  border-radius: 1rem;
  box-shadow: 0 4px 16px rgba(139, 115, 85, 0.1);
}

/* Progress Bar Section */
.progress-bar-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #654321;
}

.progress-percent {
  font-size: 1.25rem;
  font-weight: 700;
  color: #8b7355;
}

.progress-bar-track {
  height: 1rem;
  background: rgba(210, 180, 140, 0.3);
  border-radius: 0.5rem;
  overflow: hidden;
  position: relative;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #d2b48c, #daa520);
  border-radius: 0.5rem;
  transition: width 0.5s ease;
  position: relative;
  overflow: hidden;
}

.progress-glow {
  position: absolute;
  top: 0;
  right: 0;
  width: 50px;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.5));
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.progress-details {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #8b7355;
}

/* Badges Section */
.badges-section {
  padding: 1rem 0;
  border-top: 2px solid rgba(139, 115, 85, 0.2);
}

.badges-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: #654321;
  margin: 0 0 1rem 0;
}

.badges-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.35rem;
}

.badge-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.15rem;
  padding: 0.25rem;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid #d2b48c;
  border-radius: 0.4rem;
  transition: all 0.3s ease;
  min-height: 50px;
}

.badge-card.earned {
  background: linear-gradient(135deg, rgba(210, 180, 140, 0.3), rgba(218, 165, 32, 0.3));
  border-color: #daa520;
  box-shadow: 0 4px 12px rgba(218, 165, 32, 0.3);
}

.badge-card.earned .badge-icon {
  transform: scale(1.2);
  animation: badge-pop 0.5s ease;
}

@keyframes badge-pop {
  0%, 100% {
    transform: scale(1.2);
  }
  50% {
    transform: scale(1.4);
  }
}

.badge-card.locked {
  opacity: 0.5;
  filter: grayscale(1);
}

.badge-icon {
  font-size: 0.85rem;
  transition: transform 0.3s ease;
}

.badge-name {
  font-size: 0.5rem;
  font-weight: 600;
  color: #654321;
  text-align: center;
  line-height: 1;
  max-width: 100%;
  word-wrap: break-word;
}

.badge-earned-indicator {
  position: absolute;
  top: -0.1rem;
  right: -0.1rem;
  width: 0.75rem;
  height: 0.75rem;
  background: #10b981;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.45rem;
  font-weight: 700;
  box-shadow: 0 1px 4px rgba(16, 185, 129, 0.4);
}

/* Stats Section */
.stats-section {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding: 0.75rem 0;
  border-top: 2px solid rgba(139, 115, 85, 0.2);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.3rem 0.4rem;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 0.4rem;
  border: 1px solid rgba(139, 115, 85, 0.2);
}

.stat-icon {
  font-size: 0.75rem;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-value {
  font-size: 0.7rem;
  font-weight: 700;
  color: #654321;
  line-height: 1;
}

.stat-label {
  font-size: 0.5rem;
  color: #8b7355;
  margin-top: 0.1rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Motivational Message */
.motivation-message {
  position: fixed;
  top: 2rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #d2b48c, #daa520);
  color: white;
  border-radius: 1rem;
  box-shadow: 0 8px 24px rgba(139, 115, 85, 0.4);
  font-weight: 600;
  animation: slide-in-bounce 0.5s ease;
}

@keyframes slide-in-bounce {
  0% {
    transform: translateX(-50%) translateY(-100px);
    opacity: 0;
  }
  60% {
    transform: translateX(-50%) translateY(10px);
    opacity: 1;
  }
  100% {
    transform: translateX(-50%) translateY(0);
  }
}

.motivation-icon {
  font-size: 2rem;
}

.motivation-text {
  font-size: 1rem;
}

.message-fade-enter-active,
.message-fade-leave-active {
  transition: all 0.3s ease;
}

.message-fade-enter-from,
.message-fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}
</style>
