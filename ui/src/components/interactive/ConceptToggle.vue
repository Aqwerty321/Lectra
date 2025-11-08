<template>
  <div class="concept-toggle-wrapper">
    <div class="toggle-header">
      <h3>{{ data.title || 'Toggle Concept' }}</h3>
    </div>
    
    <div class="toggle-controls">
      <button
        v-for="(option, index) in data.options"
        :key="index"
        @click="selectOption(index)"
        class="toggle-btn"
        :class="{ active: selectedIndex === index }"
      >
        <span class="toggle-icon">{{ option.icon || '📌' }}</span>
        <span class="toggle-label">{{ option.label }}</span>
      </button>
    </div>
    
    <transition name="content-fade" mode="out-in">
      <div :key="selectedIndex" class="toggle-content">
        <div class="content-visual" :style="visualStyle">
          <div class="visual-emoji">{{ currentOption.emoji || '🎯' }}</div>
        </div>
        <div class="content-description">
          <h4>{{ currentOption.label }}</h4>
          <p>{{ currentOption.description }}</p>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  data: {
    type: Object,
    required: true,
    default: () => ({
      title: 'Concept Toggle',
      options: [
        { label: 'Option A', description: 'Description A', emoji: '🅰️', icon: '1️⃣', color: '#10b981' },
        { label: 'Option B', description: 'Description B', emoji: '🅱️', icon: '2️⃣', color: '#f59e0b' }
      ]
    })
  }
})

const emit = defineEmits(['update'])

const selectedIndex = ref(0)

const currentOption = computed(() => props.data.options[selectedIndex.value] || props.data.options[0])

const visualStyle = computed(() => ({
  background: `linear-gradient(135deg, ${currentOption.value.color || '#8b7355'}, ${lightenColor(currentOption.value.color || '#8b7355', 20)})`,
  transition: 'all 0.4s ease'
}))

function selectOption(index) {
  selectedIndex.value = index
  emit('update', {
    selectedIndex: index,
    option: currentOption.value
  })
}

function lightenColor(color, percent) {
  const num = parseInt(color.replace('#', ''), 16)
  const amt = Math.round(2.55 * percent)
  const R = (num >> 16) + amt
  const G = (num >> 8 & 0x00FF) + amt
  const B = (num & 0x0000FF) + amt
  return '#' + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
    (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
    (B < 255 ? B < 1 ? 0 : B : 255))
    .toString(16)
    .slice(1)
}
</script>

<style scoped>
.concept-toggle-wrapper {
  width: 100%;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 1rem;
  border: 2px solid #d2b48c;
}

.toggle-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #654321;
  margin: 0 0 1.5rem 0;
}

.toggle-controls {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.toggle-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: rgba(255, 255, 255, 0.9);
  border: 2px solid #d2b48c;
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
  font-weight: 500;
  color: #654321;
}

.toggle-btn:hover {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(139, 115, 85, 0.2);
}

.toggle-btn.active {
  background: linear-gradient(135deg, #d2b48c, #daa520);
  border-color: #8b7355;
  color: white;
  box-shadow: 0 4px 16px rgba(139, 115, 85, 0.3);
}

.toggle-icon {
  font-size: 1.25rem;
}

.toggle-content {
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 0.75rem;
  border: 2px dashed #d2b48c;
}

.content-visual {
  padding: 2rem;
  border-radius: 0.75rem;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 120px;
}

.visual-emoji {
  font-size: 5rem;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.2));
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.content-description h4 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #654321;
  margin: 0 0 0.75rem 0;
}

.content-description p {
  margin: 0;
  color: #654321;
  line-height: 1.6;
  font-size: 1rem;
}

.content-fade-enter-active,
.content-fade-leave-active {
  transition: all 0.3s ease;
}

.content-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.content-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
