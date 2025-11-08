<template>
  <div class="min-h-screen bg-dark-wood">
    <!-- Navbar -->
    <NavBar @navigate="scrollTo" />

    <!-- Hero Section -->
    <section id="home" class="min-h-screen flex items-center justify-center">
      <HeroLogo @generate="handleGenerateClick" />
    </section>

    <!-- Features Section -->
    <section id="features" class="py-20">
      <div class="container mx-auto px-6">
        <div class="bg-light-wood rounded-3xl p-12 shadow-2xl fade-section" ref="featuresSection">
          <h2 class="text-4xl font-bold text-center mb-16 text-amber-950">Features</h2>
          <FeatureCards />
        </div>
      </div>
    </section>

    <!-- Tech Stack Section -->
    <section id="tech" class="py-20">
      <div class="container mx-auto px-6">
        <h2 class="text-4xl font-bold text-center mb-16 text-amber-100">Tech Stack</h2>
        <TechStack />
      </div>
    </section>

    <!-- Generator Section -->
    <section id="generate" class="py-20">
      <div class="container mx-auto px-6">
        <div class="bg-light-wood rounded-3xl p-12 shadow-2xl fade-section" ref="generateSection">
          <h2 class="text-4xl font-bold text-center mb-16 text-red-950">Generate Audio</h2>
          <GeneratorPanel 
            :sidecar-ready="sidecarReady"
            :initial-lang="selectedLang"
            @status="handleStatus"
          />
        </div>
      </div>
    </section>

    <!-- Document Notebook Section (NEW!) -->
    <section id="notebook" class="py-20">
      <div class="container mx-auto px-6">
        <DocumentNotebook />
      </div>
    </section>

    <!-- Details Section -->
    <section id="details" class="py-20">
      <div class="container mx-auto px-6 max-w-4xl">
        <h2 class="text-4xl font-bold text-center mb-12 text-amber-100">How It Works</h2>
        <div class="glass-card p-8" style="color: #f5deb3;">
          <ol class="space-y-6 list-decimal list-inside">
            <li class="text-lg font-medium">
              <strong class="font-bold">Nuance Tagging:</strong> Ollama (llama3.1) analyzes your text and adds prosody tags
              for natural speech variations (rate, pitch, pauses).
            </li>
            <li class="text-lg font-medium">
              <strong class="font-bold">Segment Generation:</strong> Text is split into sentences, each with custom prosody settings.
            </li>
            <li class="text-lg font-medium">
              <strong class="font-bold">TTS Synthesis:</strong> Microsoft EdgeTTS generates audio for each segment with
              voice-specific adjustments.
            </li>
            <li class="text-lg font-medium">
              <strong class="font-bold">Audio Assembly:</strong> Segments are concatenated with strategic pauses using pydub.
            </li>
            <li class="text-lg font-medium">
              <strong class="font-bold">Timing Estimation:</strong> Deterministic formula calculates per-sentence start/end times
              without audio analysis.
            </li>
            <li class="text-lg">
              <strong>Output:</strong> Final MP3, timing JSON, VTT subtitles, and SSML saved to
              <code class="bg-gray-200 px-2 py-1 rounded text-gray-900">~/Lectures/&lt;project&gt;/</code>
            </li>
          </ol>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <FooterMadeWithLove />

    <!-- Status Toast -->
    <div 
      v-if="statusMessage"
      class="fixed top-4 right-4 glass-card p-4 animate-fade-in z-50"
      :class="statusType === 'error' ? 'border-red-500' : 'border-green-500'"
    >
      <p class="text-sm" :class="statusType === 'error' ? 'text-red-700' : 'text-green-700'">
        {{ statusMessage }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { fetch as tauriFetch } from '@tauri-apps/api/http'
import NavBar from './components/NavBar.vue'
import HeroLogo from './components/HeroLogo.vue'
import FeatureCards from './components/FeatureCards.vue'
import TechStack from './components/TechStack.vue'
import GeneratorPanel from './components/GeneratorPanel.vue'
import DocumentNotebook from './components/DocumentNotebook.vue'
import FooterMadeWithLove from './components/FooterMadeWithLove.vue'

const sidecarReady = ref(false)
const selectedLang = ref('en')
const statusMessage = ref('')
const statusType = ref('info')

// Refs for fade sections
const featuresSection = ref(null)
const generateSection = ref(null)

onMounted(async () => {
  // Wait a moment for everything to load
  await new Promise(resolve => setTimeout(resolve, 500))
  
  // Check sidecar health
  try {
    console.log('Starting sidecar health check...')
    await checkSidecarHealth()
    console.log('Sidecar health check completed successfully')
  } catch (err) {
    console.error('Sidecar health check failed:', err)
    showStatus('Sidecar not ready. Check that Python sidecar is running.', 'error')
    sidecarReady.value = false
  }

  // Setup scroll observer for fade animations
  setupScrollObserver()
})

onUnmounted(() => {
  if (scrollObserver) {
    scrollObserver.disconnect()
  }
})

let scrollObserver = null

function setupScrollObserver() {
  const options = {
    root: null,
    rootMargin: '-10% 0px -10% 0px',
    threshold: [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
  }

  scrollObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      // Calculate opacity based on intersection ratio
      // Make it fade in more aggressively
      const opacity = Math.min(entry.intersectionRatio * 1.5, 1)
      entry.target.style.opacity = opacity.toString()
    })
  }, options)

  // Observe fade sections
  if (featuresSection.value) {
    scrollObserver.observe(featuresSection.value)
  }
  if (generateSection.value) {
    scrollObserver.observe(generateSection.value)
  }
}

async function checkSidecarHealth() {
  const maxRetries = 10
  for (let i = 0; i < maxRetries; i++) {
    try {
      console.log(`Health check attempt ${i + 1}/${maxRetries}...`)
      const response = await tauriFetch('http://127.0.0.1:8765/healthz', {
        method: 'GET',
        responseType: 1 // JSON response type
      })
      console.log('Health check response:', response.status, response.ok)
      if (response.ok && response.data) {
        console.log('Health check data:', response.data)
        sidecarReady.value = true
        showStatus('Sidecar ready!', 'success')
        return
      }
    } catch (err) {
      console.warn(`Health check attempt ${i + 1} failed:`, err.message || err)
      // Retry
    }
    await new Promise(resolve => setTimeout(resolve, 1000))
  }
  console.error('Sidecar health check timeout after', maxRetries, 'attempts')
  throw new Error('Sidecar health check timeout')
}

function scrollTo(section) {
  const element = document.getElementById(section)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth' })
  }
}

function handleGenerateClick(lang) {
  selectedLang.value = lang
  scrollTo('generate')
}

function handleStatus(message, type = 'info') {
  showStatus(message, type)
}

function showStatus(message, type = 'info') {
  statusMessage.value = message
  statusType.value = type
  setTimeout(() => {
    statusMessage.value = ''
  }, 5000)
}
</script>
