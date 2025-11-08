<template>
  <div class="fixed bottom-4 right-4 z-50">
    <!-- Main Status Card -->
    <transition name="slide-up">
      <div
        v-if="visible"
        class="bg-white rounded-xl shadow-2xl p-4 max-w-sm border-l-4"
        :class="borderColor"
      >
        <div class="flex items-start gap-3">
          <!-- Icon -->
          <div class="flex-shrink-0">
            <div v-if="type === 'loading'" class="animate-spin text-2xl">⏳</div>
            <div v-else-if="type === 'success'" class="text-2xl">✅</div>
            <div v-else-if="type === 'error'" class="text-2xl">❌</div>
            <div v-else-if="type === 'info'" class="text-2xl">ℹ️</div>
            <div v-else class="text-2xl">💬</div>
          </div>

          <!-- Content -->
          <div class="flex-1 min-w-0">
            <h4 v-if="title" class="font-semibold text-gray-900 mb-1">{{ title }}</h4>
            <p class="text-sm text-gray-600">{{ message }}</p>
            
            <!-- Progress Bar -->
            <div v-if="progress !== null" class="mt-2">
              <div class="flex justify-between text-xs text-gray-500 mb-1">
                <span>{{ progress }}%</span>
                <span v-if="duration">{{ formatDuration(duration) }}</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div
                  class="h-2 rounded-full transition-all duration-300"
                  :class="progressColor"
                  :style="{ width: progress + '%' }"
                ></div>
              </div>
            </div>
          </div>

          <!-- Close Button -->
          <button
            v-if="closeable"
            @click="close"
            class="flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
          >
            ✕
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'info',
    validator: (value) => ['info', 'success', 'error', 'warning', 'loading'].includes(value)
  },
  title: {
    type: String,
    default: ''
  },
  message: {
    type: String,
    required: true
  },
  duration: {
    type: Number,
    default: null
  },
  progress: {
    type: Number,
    default: null
  },
  closeable: {
    type: Boolean,
    default: true
  },
  autoClose: {
    type: Number,
    default: 5000 // 5 seconds
  }
})

const emit = defineEmits(['close'])

const visible = ref(true)
let autoCloseTimer = null

const borderColor = computed(() => {
  switch (props.type) {
    case 'success': return 'border-green-500'
    case 'error': return 'border-red-500'
    case 'warning': return 'border-yellow-500'
    case 'loading': return 'border-blue-500'
    default: return 'border-gray-300'
  }
})

const progressColor = computed(() => {
  switch (props.type) {
    case 'success': return 'bg-green-500'
    case 'error': return 'bg-red-500'
    case 'warning': return 'bg-yellow-500'
    case 'loading': return 'bg-blue-500'
    default: return 'bg-gray-500'
  }
})

function close() {
  visible.value = false
  emit('close')
}

function formatDuration(ms) {
  const seconds = Math.floor(ms / 1000)
  if (seconds < 60) return `${seconds}s`
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes}m ${remainingSeconds}s`
}

// Auto-close for non-loading types
watch(() => props.type, (newType) => {
  if (newType !== 'loading' && props.autoClose > 0) {
    if (autoCloseTimer) clearTimeout(autoCloseTimer)
    autoCloseTimer = setTimeout(close, props.autoClose)
  }
}, { immediate: true })

// Clear timer on unmount
onUnmounted(() => {
  if (autoCloseTimer) clearTimeout(autoCloseTimer)
})
</script>

<style scoped>
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from {
  transform: translateY(100px);
  opacity: 0;
}

.slide-up-leave-to {
  transform: translateX(100px);
  opacity: 0;
}
</style>
