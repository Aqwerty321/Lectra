<template>
  <div class="slide-content-container" ref="containerRef">
    <!-- Actual Slide Image Background -->
    <div class="slide-image-backdrop" v-if="slideImageSrc">
      <img :src="slideImageSrc" :alt="`Slide ${slideIndex + 1}`" class="slide-bg-image" />
      <div class="slide-image-overlay"></div>
    </div>

    <!-- Fallback: Traditional Animated Content -->
    <div class="slide-content-overlay" :class="{ 'with-image': slideImageSrc }">
      <!-- Slide Title with Animation -->
      <div v-if="slide.title && !slideImageSrc" class="slide-title" ref="titleRef">
        <h1>{{ slide.title }}</h1>
      </div>

      <!-- Animated Content Items -->
      <div class="content-items-wrapper" ref="contentRef">
        <div
          v-for="(item, index) in slide.steps"
          :key="`step-${index}`"
          :ref="el => setItemRef(el, index)"
          class="content-item"
          :class="[
            `content-${item.element || 'bullet'}`,
            { 'highlighted': index === highlightedIndex },
            { 'interactive': item.interactive }
          ]"
        >
          <!-- Bullet Point -->
          <div v-if="item.element === 'bullet'" class="bullet-wrapper">
            <span class="bullet-icon">●</span>
            <div class="bullet-content">
              <span v-html="highlightKeywords(item.text)"></span>
              
              <!-- Interactive Hotspot -->
              <button
                v-if="hasHotspot(item.text)"
                @click="showTooltip(item, $event)"
                class="hotspot-btn"
                title="Click for more info"
              >
                💡
              </button>
            </div>
          </div>

          <!-- Text Paragraph -->
          <div v-else-if="item.element === 'text'" class="text-content">
            <p v-html="highlightKeywords(item.text)"></p>
          </div>

          <!-- Heading -->
          <div v-else-if="item.element === 'heading'" class="heading-content">
            <h2>{{ item.text }}</h2>
          </div>

          <!-- Image -->
          <div v-else-if="item.element === 'image'" class="image-content">
            <img :src="item.src" :alt="item.alt || 'Slide image'" />
            <p v-if="item.caption" class="image-caption">{{ item.caption }}</p>
          </div>

          <!-- Interactive Element (Simulation) -->
          <div v-else-if="item.element === 'interactive'" class="interactive-content">
            <component
              :is="getInteractiveComponent(item.type)"
              :data="item.data"
              @update="handleInteractiveUpdate"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Tooltip Popup -->
    <Transition name="tooltip-fade">
      <div
        v-if="showingTooltip"
        class="tooltip-popup glass-panel"
        :style="tooltipStyle"
        @click="closeTooltip"
      >
        <div class="tooltip-header">
          <span class="tooltip-icon">💡</span>
          <h4>{{ tooltipData.title }}</h4>
          <button @click.stop="closeTooltip" class="tooltip-close">✕</button>
        </div>
        <div class="tooltip-body">
          <p>{{ tooltipData.content }}</p>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, markRaw, computed } from 'vue'
import { gsap } from 'gsap'
import { convertFileSrc } from '@tauri-apps/api/tauri'
import ConceptSlider from './ConceptSlider.vue'
import ConceptToggle from './ConceptToggle.vue'

const props = defineProps({
  slide: {
    type: Object,
    required: true
  },
  slideIndex: {
    type: Number,
    default: 0
  },
  projectName: {
    type: String,
    default: ''
  },
  autoPlay: {
    type: Boolean,
    default: false
  },
  currentStep: {
    type: Number,
    default: 0
  },
  highlightedIndex: {
    type: Number,
    default: -1
  }
})

const emit = defineEmits(['stepComplete', 'interactionUpdate'])

// Refs
const containerRef = ref(null)
const titleRef = ref(null)
const contentRef = ref(null)
const itemRefs = ref([])
const showingTooltip = ref(false)
const tooltipData = ref({ title: '', content: '' })
const tooltipStyle = ref({})
const slideImageSrc = ref(null)

// Timeline
let timeline = null

// Computed: Load slide image from backend
const loadSlideImage = async () => {
  if (!props.projectName || props.slideIndex === undefined) return
  
  try {
    const response = await fetch(
      `http://127.0.0.1:8765/get_slide_image?project=${encodeURIComponent(props.projectName)}&slide_index=${props.slideIndex}`
    )
    
    if (response.ok) {
      const data = await response.json()
      if (data.slide_path) {
        // Convert to Tauri file protocol
        slideImageSrc.value = convertFileSrc(data.slide_path)
        console.log('✅ Loaded slide image:', slideImageSrc.value)
      }
    } else {
      console.warn('⚠️ Slide image not found, using text-based display')
      slideImageSrc.value = null
    }
  } catch (error) {
    console.warn('⚠️ Could not load slide image:', error)
    slideImageSrc.value = null
  }
}

// Watch for slide changes
watch(() => [props.slideIndex, props.projectName], () => {
  loadSlideImage()
}, { immediate: true })

// Keywords that should be clickable hotspots
const keywords = {
  'stress': { title: 'Stress', content: 'A physical, mental, or emotional factor that causes bodily or mental tension.' },
  'neuron': { title: 'Neuron', content: 'A specialized cell transmitting nerve impulses; a nerve cell.' },
  'psychology': { title: 'Psychology', content: 'The scientific study of the human mind and its functions.' },
  'cognitive': { title: 'Cognitive', content: 'Related to the mental action or process of acquiring knowledge and understanding.' },
  'behavior': { title: 'Behavior', content: 'The way in which one acts or conducts oneself, especially toward others.' }
}

// Methods
function setItemRef(el, index) {
  if (el) {
    itemRefs.value[index] = el
  }
}

function highlightKeywords(text) {
  if (!text) return ''
  
  let result = text
  Object.keys(keywords).forEach(keyword => {
    const regex = new RegExp(`\\b(${keyword})\\b`, 'gi')
    result = result.replace(regex, '<span class="keyword-highlight" data-keyword="$1">$1</span>')
  })
  return result
}

function hasHotspot(text) {
  if (!text) return false
  return Object.keys(keywords).some(keyword => 
    text.toLowerCase().includes(keyword.toLowerCase())
  )
}

function showTooltip(item, event) {
  const target = event.target
  const rect = target.getBoundingClientRect()
  
  // Find keyword in text
  const text = item.text.toLowerCase()
  const foundKeyword = Object.keys(keywords).find(k => text.includes(k.toLowerCase()))
  
  if (foundKeyword) {
    tooltipData.value = keywords[foundKeyword]
    tooltipStyle.value = {
      top: `${rect.top - 100}px`,
      left: `${rect.left}px`
    }
    showingTooltip.value = true
  }
}

function closeTooltip() {
  showingTooltip.value = false
}

function getInteractiveComponent(type) {
  const components = {
    'slider': markRaw(ConceptSlider),
    'toggle': markRaw(ConceptToggle)
  }
  return components[type] || null
}

function handleInteractiveUpdate(data) {
  emit('interactionUpdate', data)
}

function createTimeline() {
  if (!containerRef.value) return
  
  // Kill existing timeline
  if (timeline) {
    timeline.kill()
  }
  
  // Create new timeline
  timeline = gsap.timeline({ paused: true })
  
  // Animate title first
  if (titleRef.value) {
    timeline.from(titleRef.value, {
      opacity: 0,
      y: -30,
      duration: 0.6,
      ease: 'power2.out'
    })
  }
  
  // Animate each content item
  itemRefs.value.forEach((item, index) => {
    if (item) {
      timeline.from(item, {
        opacity: 0,
        y: 20,
        x: -10,
        duration: 0.5,
        ease: 'power2.out',
        onComplete: () => {
          emit('stepComplete', index)
        }
      }, index === 0 ? '+=0.2' : '+=0.3')
    }
  })
  
  return timeline
}

function playStep(stepIndex) {
  if (!timeline) return
  
  const stepDuration = 0.5
  const targetTime = stepIndex * stepDuration
  
  gsap.to(timeline, {
    time: targetTime,
    duration: 0.3,
    ease: 'power2.inOut'
  })
}

function playAllSteps() {
  if (timeline) {
    timeline.play()
  }
}

function resetAnimation() {
  if (timeline) {
    timeline.seek(0)
  }
}

// Watchers
watch(() => props.currentStep, (newStep) => {
  playStep(newStep)
})

watch(() => props.slide, () => {
  nextTick(() => {
    createTimeline()
    if (props.autoPlay) {
      playAllSteps()
    }
  })
}, { immediate: true })

// Lifecycle
onMounted(() => {
  nextTick(() => {
    createTimeline()
    
    if (props.autoPlay) {
      setTimeout(() => {
        playAllSteps()
      }, 300)
    }
    
    // Add click listeners for keyword highlights
    if (contentRef.value) {
      contentRef.value.addEventListener('click', (e) => {
        if (e.target.classList.contains('keyword-highlight')) {
          const keyword = e.target.dataset.keyword
          if (keywords[keyword.toLowerCase()]) {
            const rect = e.target.getBoundingClientRect()
            tooltipData.value = keywords[keyword.toLowerCase()]
            tooltipStyle.value = {
              top: `${rect.bottom + 10}px`,
              left: `${rect.left}px`
            }
            showingTooltip.value = true
          }
        }
      })
    }
  })
})

// Expose methods
defineExpose({
  playStep,
  playAllSteps,
  resetAnimation
})
</script>

<style scoped>
.slide-content-container {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Slide Image Backdrop */
.slide-image-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

.slide-bg-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  object-position: center;
}

.slide-image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    to bottom,
    rgba(26, 26, 26, 0.05) 0%,
    rgba(26, 26, 26, 0.02) 50%,
    rgba(26, 26, 26, 0.05) 100%
  );
  pointer-events: none;
}

/* Content Overlay */
.slide-content-overlay {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 2rem;
  overflow-y: auto;
}

.slide-content-overlay.with-image {
  /* When showing real slide image, make overlays more subtle */
  background: rgba(245, 230, 211, 0.05);
}

.slide-content-overlay.with-image .content-item {
  /* Reduce visibility of text overlays when actual slide is shown */
  opacity: 0;
  pointer-events: none;
}

.slide-content-overlay.with-image .content-item.highlighted {
  /* Highlight current step with glowing effect */
  opacity: 1;
  pointer-events: auto;
  background: rgba(255, 215, 0, 0.2);
  border-left: 4px solid #FFD700;
  padding-left: 1.5rem;
  padding-right: 1rem;
  padding-top: 0.75rem;
  padding-bottom: 0.75rem;
  border-radius: 0.5rem;
  box-shadow: 0 0 20px rgba(255, 215, 0, 0.4);
  backdrop-filter: blur(8px);
  margin-bottom: 0.5rem;
}

.slide-title h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: #654321;
  text-align: center;
  margin-bottom: 2rem;
  text-shadow: 2px 2px 4px rgba(101, 67, 33, 0.1);
}

.content-items-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.content-item {
  opacity: 0;
  transition: all 0.3s ease;
}

.content-item.highlighted {
  background: rgba(255, 237, 213, 0.5);
  border-radius: 0.75rem;
  padding: 0.5rem;
  box-shadow: 0 0 0 3px rgba(139, 115, 85, 0.3);
}

/* Bullet Points */
.bullet-wrapper {
  display: flex;
  align-items: start;
  gap: 1rem;
  padding: 1rem 1.5rem;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 0.75rem;
  border-left: 4px solid #d2b48c;
  transition: all 0.3s ease;
  position: relative;
}

.bullet-wrapper:hover {
  background: rgba(255, 255, 255, 0.95);
  transform: translateX(5px);
  box-shadow: 0 4px 12px rgba(139, 115, 85, 0.15);
}

.bullet-icon {
  color: #8b7355;
  font-size: 1.25rem;
  flex-shrink: 0;
  margin-top: 0.25rem;
}

.bullet-content {
  flex: 1;
  color: #654321;
  font-size: 1.125rem;
  line-height: 1.7;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

/* Keyword Highlighting */
.keyword-highlight {
  color: #d97706;
  font-weight: 600;
  cursor: pointer;
  border-bottom: 2px dotted #d97706;
  transition: all 0.2s ease;
  position: relative;
}

.keyword-highlight:hover {
  color: #b45309;
  border-bottom-color: #b45309;
  background: rgba(217, 119, 6, 0.1);
  padding: 0 0.25rem;
  border-radius: 0.25rem;
}

/* Hotspot Button */
.hotspot-btn {
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  border: none;
  border-radius: 50%;
  width: 2rem;
  height: 2rem;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
  animation: pulse-glow 2s ease-in-out infinite;
}

.hotspot-btn:hover {
  transform: scale(1.15);
  box-shadow: 0 4px 16px rgba(245, 158, 11, 0.5);
}

@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
  }
  50% {
    box-shadow: 0 4px 16px rgba(245, 158, 11, 0.6);
  }
}

/* Text Content */
.text-content p {
  padding: 1rem 1.5rem;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 0.75rem;
  color: #654321;
  font-size: 1.125rem;
  line-height: 1.7;
}

/* Heading */
.heading-content h2 {
  font-size: 1.75rem;
  font-weight: 600;
  color: #8b7355;
  margin: 1.5rem 0 1rem;
}

/* Image */
.image-content {
  margin: 1.5rem 0;
  text-align: center;
}

.image-content img {
  max-width: 100%;
  height: auto;
  border-radius: 1rem;
  box-shadow: 0 8px 24px rgba(139, 115, 85, 0.2);
  transition: transform 0.3s ease;
}

.image-content img:hover {
  transform: scale(1.02);
}

.image-caption {
  margin-top: 0.75rem;
  font-size: 0.95rem;
  color: #8b7355;
  font-style: italic;
}

/* Interactive Content */
.interactive-content {
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 1rem;
  box-shadow: 0 4px 16px rgba(139, 115, 85, 0.15);
}

/* Tooltip Popup */
.tooltip-popup {
  position: fixed;
  z-index: 100;
  max-width: 320px;
  padding: 0;
  overflow: hidden;
  cursor: pointer;
}

.tooltip-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  background: linear-gradient(135deg, #d2b48c, #daa520);
  color: white;
}

.tooltip-icon {
  font-size: 1.5rem;
}

.tooltip-header h4 {
  flex: 1;
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
}

.tooltip-close {
  background: none;
  border: none;
  color: white;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0;
  width: 1.5rem;
  height: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.25rem;
  transition: background 0.2s ease;
}

.tooltip-close:hover {
  background: rgba(255, 255, 255, 0.2);
}

.tooltip-body {
  padding: 1.25rem;
  background: white;
}

.tooltip-body p {
  margin: 0;
  color: #654321;
  line-height: 1.6;
  font-size: 1rem;
}

/* Transitions */
.tooltip-fade-enter-active,
.tooltip-fade-leave-active {
  transition: all 0.3s ease;
}

.tooltip-fade-enter-from {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}

.tooltip-fade-leave-to {
  opacity: 0;
  transform: translateY(10px) scale(0.95);
}

.glass-panel {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: 1rem;
  box-shadow: 0 8px 32px rgba(139, 115, 85, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.5);
}
</style>
