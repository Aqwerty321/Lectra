<template>
  <div class="concept-slider-wrapper">
    <div class="slider-header">
      <h3>{{ data.title || 'Interactive Concept' }}</h3>
      <span class="slider-value">{{ currentValue }}{{ data.unit || '' }}</span>
    </div>
    
    <div class="slider-visualization" :style="visualizationStyle">
      <div class="visual-indicator" :style="indicatorStyle">
        {{ getEmoji() }}
      </div>
    </div>
    
    <div class="slider-control">
      <span class="slider-label-min">{{ data.min || 0 }}</span>
      <input
        type="range"
        v-model="currentValue"
        :min="data.min || 0"
        :max="data.max || 100"
        :step="data.step || 1"
        class="slider-input"
        @input="handleChange"
      />
      <span class="slider-label-max">{{ data.max || 100 }}</span>
    </div>
    
    <div class="slider-description">
      <p>{{ getDescription() }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  data: {
    type: Object,
    required: true,
    default: () => ({
      title: 'Concept Explorer',
      min: 0,
      max: 100,
      step: 1,
      unit: '',
      type: 'stress' // stress, temperature, speed, etc.
    })
  }
})

const emit = defineEmits(['update'])

const currentValue = ref(props.data.initial || 50)

const visualizationStyle = computed(() => {
  const percent = ((currentValue.value - (props.data.min || 0)) / ((props.data.max || 100) - (props.data.min || 0))) * 100
  
  // Color gradient based on value
  let backgroundColor
  if (percent < 33) {
    backgroundColor = 'linear-gradient(135deg, #10b981, #34d399)'
  } else if (percent < 66) {
    backgroundColor = 'linear-gradient(135deg, #f59e0b, #fbbf24)'
  } else {
    backgroundColor = 'linear-gradient(135deg, #ef4444, #f87171)'
  }
  
  return {
    background: backgroundColor,
    height: `${Math.max(100, percent * 2)}px`,
    transition: 'all 0.4s ease'
  }
})

const indicatorStyle = computed(() => {
  const percent = ((currentValue.value - (props.data.min || 0)) / ((props.data.max || 100) - (props.data.min || 0))) * 100
  return {
    transform: `scale(${0.8 + percent / 100})`,
    transition: 'transform 0.3s ease'
  }
})

function getEmoji() {
  const percent = ((currentValue.value - (props.data.min || 0)) / ((props.data.max || 100) - (props.data.min || 0))) * 100
  
  const emojiMap = {
    stress: percent < 33 ? '😌' : percent < 66 ? '😰' : '😵',
    temperature: percent < 33 ? '🥶' : percent < 66 ? '😊' : '🥵',
    speed: percent < 33 ? '🐢' : percent < 66 ? '🚶' : '🏃',
    mood: percent < 33 ? '😢' : percent < 66 ? '😐' : '😄'
  }
  
  return emojiMap[props.data.type] || '📊'
}

function getDescription() {
  const percent = ((currentValue.value - (props.data.min || 0)) / ((props.data.max || 100) - (props.data.min || 0))) * 100
  
  const descriptionMap = {
    stress: {
      low: 'Low stress levels promote clear thinking and creativity.',
      medium: 'Moderate stress can enhance performance but requires management.',
      high: 'High stress impairs cognitive function and decision-making.'
    },
    temperature: {
      low: 'Cold temperature slows molecular movement.',
      medium: 'Optimal temperature for most reactions.',
      high: 'High temperature increases molecular activity.'
    },
    speed: {
      low: 'Slow and steady allows for careful observation.',
      medium: 'Moderate pace balances speed and accuracy.',
      high: 'High speed requires quick reflexes and decisions.'
    }
  }
  
  const map = descriptionMap[props.data.type] || {
    low: 'Lower values',
    medium: 'Medium values',
    high: 'Higher values'
  }
  
  if (percent < 33) return map.low
  if (percent < 66) return map.medium
  return map.high
}

function handleChange() {
  emit('update', {
    value: currentValue.value,
    type: props.data.type
  })
}

watch(currentValue, () => {
  handleChange()
})
</script>

<style scoped>
.concept-slider-wrapper {
  width: 100%;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 1rem;
  border: 2px solid #d2b48c;
}

.slider-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.slider-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #654321;
  margin: 0;
}

.slider-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #8b7355;
  padding: 0.25rem 0.75rem;
  background: rgba(139, 115, 85, 0.1);
  border-radius: 0.5rem;
}

.slider-visualization {
  margin: 1.5rem 0;
  border-radius: 1rem;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100px;
}

.visual-indicator {
  font-size: 4rem;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
}

.slider-control {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin: 1.5rem 0;
}

.slider-label-min,
.slider-label-max {
  font-size: 0.875rem;
  font-weight: 600;
  color: #8b7355;
  min-width: 2rem;
  text-align: center;
}

.slider-input {
  flex: 1;
  height: 8px;
  border-radius: 4px;
  background: linear-gradient(to right, #10b981, #f59e0b, #ef4444);
  outline: none;
  -webkit-appearance: none;
  appearance: none;
}

.slider-input::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: white;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  border: 3px solid #8b7355;
  transition: all 0.2s ease;
}

.slider-input::-webkit-slider-thumb:hover {
  transform: scale(1.2);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.slider-input::-moz-range-thumb {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: white;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  border: 3px solid #8b7355;
  transition: all 0.2s ease;
}

.slider-input::-moz-range-thumb:hover {
  transform: scale(1.2);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.slider-description {
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(210, 180, 140, 0.2);
  border-radius: 0.5rem;
  border-left: 4px solid #d2b48c;
}

.slider-description p {
  margin: 0;
  color: #654321;
  font-size: 0.95rem;
  line-height: 1.5;
  font-style: italic;
}
</style>
