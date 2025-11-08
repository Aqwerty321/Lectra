<template>
  <div class="max-w-4xl mx-auto">
    <div class="glass-card p-8">
      <!-- Status Warning -->
      <div v-if="!sidecarReady" class="mb-6 p-4 bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700">
        <p class="font-bold">⚠️ Sidecar Not Ready</p>
        <p class="text-sm">Ensure Ollama is running with llama3.1:latest model pulled.</p>
      </div>

      <!-- Project Name -->
      <div class="mb-6">
        <label class="block text-sm font-bold mb-2 text-red-950">Project Name</label>
        <input
          v-model="projectName"
          type="text"
          placeholder="my-lecture"
          class="w-full px-4 py-2 border-2 border-red-200 rounded-lg focus:ring-2 focus:ring-red-600 focus:border-transparent text-red-950 font-medium"
        />
      </div>

      <!-- Mode Selection -->
      <div class="mb-6">
        <label class="block text-sm font-bold mb-2 text-red-950">Generation Mode</label>
        <div class="flex gap-4">
          <button
            @click="generationMode = 'audio'"
            class="flex-1 px-6 py-3 rounded-lg font-bold transition-all"
            :class="generationMode === 'audio' ? 'bg-red-700 text-beige shadow-lg' : 'bg-red-100 text-red-950 hover:bg-red-200'"
          >
            🎙️ Audio Only
          </button>
          <button
            @click="generationMode = 'presentation'"
            class="flex-1 px-6 py-3 rounded-lg font-bold transition-all"
            :class="generationMode === 'presentation' ? 'bg-red-700 text-beige shadow-lg' : 'bg-red-100 text-red-950 hover:bg-red-200'"
          >
            📊 Full Presentation
          </button>
        </div>
      </div>

      <!-- Language Selection -->
      <div class="mb-6">
        <label class="block text-sm font-bold mb-2 text-red-950">Language</label>
        <div class="flex gap-4">
          <button
            @click="lang = 'en'"
            class="px-6 py-2 rounded-lg font-bold transition-all"
            :class="lang === 'en' ? 'bg-yellow-100 text-beige' : 'bg-red-100 text-red-950 hover:bg-red-200'"
          >
            English
          </button>
          <button
            @click="lang = 'hi'"
            class="px-6 py-2 rounded-lg font-bold transition-all"
            :class="lang === 'hi' ? 'bg-yellow-100 text-beige' : 'bg-red-100 text-red-950 hover:bg-red-200'"
          >
            हिंदी (Hindi)
          </button>
        </div>
      </div>

      <!-- Voice Selection -->
      <div class="mb-6">
        <label class="block text-sm font-bold mb-2 text-red-950">Voice</label>
        <select
          v-model="voice"
          class="w-full px-4 py-2 border-2 border-red-200 rounded-lg focus:ring-2 focus:ring-red-600 text-red-950 font-medium"
        >
          <option value="">Default ({{ lang === 'en' ? 'en-US-GuyNeural' : 'hi-IN-SwaraNeural' }})</option>
          <optgroup label="English Voices">
            <option value="en-US-GuyNeural">en-US-GuyNeural (Male)</option>
            <option value="en-US-AriaNeural">en-US-AriaNeural (Female)</option>
          </optgroup>
          <optgroup label="Hindi Voices">
            <option value="hi-IN-SwaraNeural">hi-IN-SwaraNeural (Female)</option>
            <option value="hi-IN-MadhurNeural">hi-IN-MadhurNeural (Male)</option>
          </optgroup>
        </select>
      </div>

      <!-- Presentation Topic (for presentation mode) -->
      <div v-if="generationMode === 'presentation'" class="mb-6">
        <label class="block text-sm font-bold mb-2 text-red-950">Presentation Topic</label>
        <input
          v-model="presentationTopic"
          type="text"
          placeholder="e.g., Artificial Intelligence in Healthcare"
          class="w-full px-4 py-2 border-2 border-red-200 rounded-lg focus:ring-2 focus:ring-red-600 focus:border-transparent text-red-950 font-medium"
        />
        <p class="text-sm text-red-800 mt-1">AI will generate slides, content, and narration from this topic</p>
      </div>

      <!-- Text Input (for audio mode) -->
      <div v-if="generationMode === 'audio'" class="mb-6">
        <label class="block text-sm font-bold mb-2 text-red-950">Input Text</label>
        <div class="mb-2">
          <button
            @click="useSample = useSample === lang ? 'none' : lang"
            class="text-sm px-4 py-2 rounded-lg transition-colors font-bold"
            :class="useSample === lang ? 'bg-red-200 text-red-950' : 'bg-red-100 text-red-900 hover:bg-red-200'"
          >
            {{ useSample === lang ? '✓ Using' : 'Use' }} Big Sample ({{ lang.toUpperCase() }})
          </button>
        </div>
        <textarea
          v-model="inputText"
          :disabled="useSample !== 'none'"
          rows="8"
          placeholder="Enter your text here or use the big sample..."
          class="w-full px-4 py-2 border-2 border-red-200 rounded-lg focus:ring-2 focus:ring-red-600 font-mono text-sm text-red-950 font-medium"
          :class="useSample !== 'none' ? 'bg-red-50' : ''"
        ></textarea>
      </div>

      <!-- Advanced Options -->
      <details class="mb-6">
        <summary class="cursor-pointer font-bold text-red-950 mb-2">⚙️ Advanced Options</summary>
        <div class="pl-4 space-y-4 mt-4">
          <div>
            <label class="block text-sm font-bold mb-1 text-red-950">Fallback Rate</label>
            <input
              v-model="fallbackRate"
              type="text"
              placeholder="-10%"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg"
            />
          </div>
          <div>
            <label class="block text-sm font-bold mb-1 text-red-950">Fallback Pitch</label>
            <input
              v-model="fallbackPitch"
              type="text"
              placeholder="+0st"
              class="w-full px-4 py-2 border-2 border-red-200 rounded-lg text-red-950 font-medium"
            />
          </div>
        </div>
      </details>

      <!-- Action Buttons -->
      <div v-if="generationMode === 'audio'" class="flex gap-4 mb-6">
        <button
          @click="handleEstimate"
          :disabled="!sidecarReady || isProcessing"
          class="flex-1 px-6 py-3 bg-red-700 text-beige rounded-lg font-bold hover:bg-red-800 disabled:bg-red-300 disabled:cursor-not-allowed transition-colors shadow-lg"
        >
          {{ isProcessing && mode === 'estimate' ? 'Estimating...' : '⏱️ Estimate Only' }}
        </button>
        <button
          @click="handleGenerate"
          :disabled="!sidecarReady || isProcessing"
          class="flex-1 px-6 py-3 bg-red-800 text-beige rounded-lg font-bold hover:bg-red-900 disabled:bg-red-300 disabled:cursor-not-allowed transition-colors shadow-lg"
        >
          {{ isProcessing && mode === 'generate' ? 'Generating...' : '🎙️ Generate Audio' }}
        </button>
      </div>

      <div v-if="generationMode === 'presentation'" class="mb-6">
        <button
          @click="handleGeneratePresentation"
          :disabled="!sidecarReady || isProcessing || !presentationTopic.trim()"
          class="w-full px-6 py-4 bg-red-800 text-beige rounded-lg font-bold hover:bg-red-900 disabled:bg-red-300 disabled:cursor-not-allowed transition-colors shadow-lg text-lg"
        >
          {{ isProcessing && mode === 'presentation' ? 'Generating Presentation...' : '📊 Generate Full Presentation' }}
        </button>
      </div>

      <!-- Progress Bar -->
      <ProgressBar v-if="isProcessing" :message="progressMessage" />

      <!-- Results -->
      <div v-if="result" class="mt-6 p-4 bg-green-50 border-2 border-green-200 rounded-lg">
        <h3 class="font-bold text-green-800 mb-2">✅ Success!</h3>
        <div class="space-y-2 text-sm text-red-950">
          <p><strong>Project:</strong> {{ result.project_dir }}</p>
          
          <!-- Presentation Results -->
          <template v-if="result.presentation_title">
            <p class="text-lg"><strong>🎉 Presentation:</strong> {{ result.presentation_title }}</p>
            <div class="grid grid-cols-2 gap-2 mt-2">
              <p><strong>📑 Slides:</strong> {{ result.slide_count }}</p>
              <p><strong>⏱️ Duration:</strong> {{ result.duration_sec }}s</p>
              <p v-if="result.image_count"><strong>🖼️ Images:</strong> {{ result.image_count }}</p>
              <p><strong>🎨 Design:</strong> Professional</p>
            </div>
            
            <!-- Features Badge -->
            <div v-if="result.features" class="mt-3 flex flex-wrap gap-2">
              <span v-for="feature in result.features" :key="feature" 
                class="px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-bold">
                ✓ {{ feature }}
              </span>
            </div>
            
            <p v-if="result.pptx_path" class="mt-2 text-xs text-gray-600"><strong>File:</strong> {{ result.pptx_path }}</p>
            <p v-if="result.audio_path" class="text-xs text-gray-600"><strong>Audio:</strong> {{ result.audio_path }}</p>
            
            <div class="flex gap-2 mt-4">
              <button
                v-if="result.pptx_path"
                @click="playAudio(result.pptx_path)"
                class="flex-1 px-4 py-3 bg-purple-600 text-beige rounded-lg hover:bg-purple-700 transition-colors font-bold shadow-lg"
              >
                📊 Open Presentation
              </button>
              <button
                v-if="result.audio_path"
                @click="playAudio(result.audio_path)"
                class="flex-1 px-4 py-3 bg-blue-600 text-beige rounded-lg hover:bg-blue-700 transition-colors font-bold shadow-lg"
              >
                ▶️ Play Narration
              </button>
            </div>
          </template>

          <!-- Audio Only Results -->
          <template v-else>
            <p><strong>Duration:</strong> {{ result.duration_sec }}s ({{ result.sentence_count }} sentences)</p>
            <p v-if="result.mp3_path"><strong>Audio:</strong> {{ result.mp3_path }}</p>
            <p><strong>Timings:</strong> {{ result.timings_path }}</p>
            <div v-if="result.tagged_preview" class="mt-2">
              <strong>Tagged Preview:</strong>
              <pre class="mt-1 p-2 bg-white rounded text-xs overflow-x-auto text-red-950">{{ result.tagged_preview }}</pre>
            </div>
            <button
              v-if="result.mp3_path"
              @click="playAudio(result.mp3_path)"
              class="mt-2 px-4 py-2 bg-blue-600 text-beige rounded-lg hover:bg-blue-700 transition-colors font-bold"
            >
              ▶️ Play Audio
            </button>
          </template>
        </div>
      </div>

      <!-- Error Display -->
      <div v-if="error" class="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
        <h3 class="font-bold text-red-800 mb-2">❌ Error</h3>
        <p class="text-sm text-red-700">{{ error }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { fetch as tauriFetch } from '@tauri-apps/api/http'
import { open } from '@tauri-apps/api/shell'
import ProgressBar from './ProgressBar.vue'

const props = defineProps({
  sidecarReady: Boolean,
  initialLang: String
})

const emit = defineEmits(['status'])

// Form state
const projectName = ref('my-lecture')
const generationMode = ref('presentation') // 'audio' or 'presentation'
const presentationTopic = ref('')
const lang = ref(props.initialLang || 'en')
const voice = ref('')
const inputText = ref('')
const useSample = ref('none')
const fallbackRate = ref('-10%')
const fallbackPitch = ref('+0st')

// Processing state
const isProcessing = ref(false)
const mode = ref('')
const progressMessage = ref('')
const result = ref(null)
const error = ref(null)

// Watch initial lang
watch(() => props.initialLang, (newLang) => {
  if (newLang) {
    lang.value = newLang
  }
})

async function handleEstimate() {
  await processRequest('estimate')
}

async function handleGenerate() {
  await processRequest('generate')
}

async function handleGeneratePresentation() {
  if (!projectName.value.trim()) {
    emit('status', 'Please enter a project name', 'error')
    return
  }

  if (!presentationTopic.value.trim()) {
    emit('status', 'Please enter a presentation topic', 'error')
    return
  }

  mode.value = 'presentation'
  isProcessing.value = true
  error.value = null
  result.value = null
  progressMessage.value = 'Generating presentation with AI...'

  try {
    const payload = {
      project: projectName.value,
      topic: presentationTopic.value,
      lang: lang.value,
      voice: voice.value || null,
      fallback_rate: fallbackRate.value,
      fallback_pitch: fallbackPitch.value
    }

    const response = await tauriFetch('http://127.0.0.1:8765/generate_presentation', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: {
        type: 'Json',
        payload
      },
      responseType: 1 // JSON response type
    })

    if (!response.ok) {
      throw new Error(response.data?.detail || 'Presentation generation failed')
    }

    result.value = response.data
    emit('status', 'Presentation generated successfully!', 'success')
  } catch (err) {
    error.value = err.message
    emit('status', `Failed: ${err.message}`, 'error')
  } finally {
    isProcessing.value = false
    progressMessage.value = ''
  }
}

async function processRequest(requestMode) {
  if (!projectName.value.trim()) {
    emit('status', 'Please enter a project name', 'error')
    return
  }

  mode.value = requestMode
  isProcessing.value = true
  error.value = null
  result.value = null
  progressMessage.value = requestMode === 'estimate' ? 'Estimating timing...' : 'Generating audio...'

  try {
    const endpoint = requestMode === 'estimate' ? '/estimate' : '/generate'
    const payload = {
      project: projectName.value,
      text: inputText.value,
      lang: lang.value,
      voice: voice.value || null,
      use_sample: useSample.value,
      fallback_rate: fallbackRate.value,
      fallback_pitch: fallbackPitch.value
    }

    const response = await tauriFetch(`http://127.0.0.1:8765${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: {
        type: 'Json',
        payload
      },
      responseType: 1 // JSON response type
    })

    if (!response.ok) {
      throw new Error(response.data?.detail || 'Request failed')
    }

    result.value = response.data
    emit('status', `${requestMode === 'estimate' ? 'Estimation' : 'Generation'} complete!`, 'success')
  } catch (err) {
    error.value = err.message
    emit('status', `Failed: ${err.message}`, 'error')
  } finally {
    isProcessing.value = false
    progressMessage.value = ''
  }
}

async function playAudio(path) {
  try {
    // Open the audio file with the default system player
    await open(path)
    emit('status', `Opening audio: ${path}`, 'success')
  } catch (err) {
    emit('status', `Failed to open audio: ${err.message}`, 'error')
  }
}
</script>
