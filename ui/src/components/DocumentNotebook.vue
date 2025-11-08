<template>
  <div class="document-notebook wood-texture rounded-2xl shadow-2xl p-8">
    <!-- Header -->
    <div class="glass-header flex items-center justify-between mb-8 p-6 rounded-xl">
      <h2 class="text-3xl font-bold text-amber-900">
        📚 Document Notebook
      </h2>
      <div class="flex gap-3">
        <button
          @click="activeTab = 'upload'"
          class="px-4 py-2 rounded-lg transition-all"
          :class="activeTab === 'upload' ? 'bg-amber-600 text-white' : 'bg-white text-amber-800 hover:bg-amber-100'"
        >
          📤 Upload
        </button>
        <button
          @click="activeTab = 'library'"
          class="px-4 py-2 rounded-lg transition-all"
          :class="activeTab === 'library' ? 'bg-amber-600 text-white' : 'bg-white text-amber-800 hover:bg-amber-100'"
        >
          📖 Library
        </button>
        <button
          @click="activeTab = 'generate'"
          class="px-4 py-2 rounded-lg transition-all"
          :class="activeTab === 'generate' ? 'bg-amber-600 text-white' : 'bg-white text-amber-800 hover:bg-amber-100'"
        >
          🎬 Generate
        </button>
        <button
          @click="activeTab = 'viewer'"
          class="px-4 py-2 rounded-lg transition-all"
          :class="activeTab === 'viewer' ? 'bg-amber-600 text-white' : 'bg-white text-amber-800 hover:bg-amber-100'"
        >
          📺 Viewer
        </button>
        <button
          @click="activeTab = 'study'"
          class="px-4 py-2 rounded-lg transition-all"
          :class="activeTab === 'study' ? 'bg-amber-600 text-white' : 'bg-white text-amber-800 hover:bg-amber-100'"
        >
          🎓 Study Mode
        </button>
        <button
          @click="activeTab = 'interactive'"
          class="px-4 py-2 rounded-lg transition-all"
          :class="activeTab === 'interactive' ? 'bg-amber-600 text-white' : 'bg-white text-amber-800 hover:bg-amber-100'"
        >
          🎭 Interactive
        </button>
      </div>
    </div>

    <!-- Upload Tab -->
    <div v-if="activeTab === 'upload'" class="space-y-6 animate-fade-in">
      <div class="glass-card rounded-xl p-6 shadow-lg backdrop-blur-xl">
        <h3 class="text-xl font-semibold text-amber-900 mb-4">📄 Upload Document</h3>
        
        <!-- Project Name -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">Project Name</label>
          <input
            v-model="projectName"
            type="text"
            placeholder="my-lecture-notes"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
          />
        </div>

        <!-- File Upload -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">Document (PDF or DOCX)</label>
          <div class="relative">
            <input
              type="file"
              @change="handleFileSelect"
              accept=".pdf,.docx"
              class="w-full px-4 py-2 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer
                     hover:border-amber-500 transition-colors file:mr-4 file:py-2 file:px-4
                     file:rounded-lg file:border-0 file:bg-amber-100 file:text-amber-700
                     file:cursor-pointer hover:file:bg-amber-200"
            />
          </div>
          <p v-if="selectedFile" class="mt-2 text-sm text-gray-600">
            Selected: {{ selectedFile.name }} ({{ formatFileSize(selectedFile.size) }})
          </p>
        </div>

        <!-- Upload Button -->
        <button
          @click="uploadDocument"
          :disabled="!selectedFile || !projectName || uploading"
          class="w-full py-3 px-6 rounded-lg font-semibold text-white transition-all transform hover:scale-105
                 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
          :class="uploading ? 'bg-gray-400' : 'bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-700 hover:to-orange-700'"
        >
          <span v-if="uploading">
            <svg class="animate-spin inline-block w-5 h-5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Processing...
          </span>
          <span v-else>🚀 Upload & Process</span>
        </button>

        <!-- Upload Error -->
        <div v-if="uploadError" class="mt-4 p-4 rounded-lg bg-red-50 border border-red-200">
          <h4 class="font-semibold text-red-900 mb-2">❌ Upload Failed</h4>
          <p class="text-sm text-red-800">{{ uploadError }}</p>
        </div>

        <!-- Upload Result -->
        <div v-if="uploadResult" class="mt-6 p-4 rounded-lg bg-green-50 border border-green-200">
          <h4 class="font-semibold text-green-900 mb-2">✅ Processing Complete!</h4>
          <div class="text-sm text-green-800 space-y-1">
            <p>📁 File: {{ uploadResult.filename }}</p>
            <p>📊 Characters: {{ uploadResult.char_count.toLocaleString() }}</p>
            <p>🔖 Chunks: {{ uploadResult.chunk_count }}</p>
            <p>📚 Collection: {{ uploadResult.collection_name }}</p>
            <p class="mt-3 font-medium">🎯 Detected Topics ({{ uploadResult.topics.length }}):</p>
            <div class="flex flex-wrap gap-2 mt-2">
              <span
                v-for="topic in uploadResult.topics.slice(0, 10)"
                :key="topic"
                class="px-2 py-1 bg-white rounded-full text-xs text-green-700 border border-green-300"
              >
                {{ topic }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Library Tab -->
    <div v-if="activeTab === 'library'" class="space-y-6 animate-fade-in">
      <div class="glass-card rounded-xl p-6 shadow-lg backdrop-blur-xl">
        <h3 class="text-xl font-semibold text-amber-900 mb-4">📖 Your Projects</h3>
        
        <!-- Refresh Button -->
        <button
          @click="loadProjects"
          class="mb-4 px-4 py-2 glass-button-amber rounded-lg transition-all"
        >
          🔄 Refresh
        </button>

        <!-- Projects Grid -->
        <div v-if="projects.length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            v-for="project in projects"
            :key="project.name"
            class="p-4 glass-project-card rounded-lg hover:scale-105 transition-all cursor-pointer"
            @click="selectProject(project)"
          >
            <h4 class="font-semibold text-lg text-amber-900 mb-2">📁 {{ project.name }}</h4>
            <div class="space-y-1 text-sm text-gray-700">
              <p v-if="project.has_video">✅ Video available</p>
              <p v-if="project.has_presentation">✅ Presentation available</p>
              <p v-if="project.collections.length > 0">
                📚 {{ project.collections.length }} document(s)
              </p>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-12 text-gray-600">
          <p class="text-lg">📭 No projects yet</p>
          <p class="text-sm mt-2">Upload a document to get started!</p>
        </div>
      </div>
    </div>

    <!-- Generate Tab -->
    <div v-if="activeTab === 'generate'" class="space-y-6 animate-fade-in">
      <div class="glass-card rounded-xl p-6 shadow-lg backdrop-blur-xl">
        <h3 class="text-xl font-semibold text-amber-900 mb-4">🎬 Generate Presentation</h3>
        
        <!-- Collection Selector -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">Select Collection</label>
          <select
            v-model="selectedCollection"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500"
          >
            <option value="">-- Choose a document --</option>
            <option
              v-for="project in projects.filter(p => p.collections.length > 0)"
              :key="project.name"
              :value="project.collections[0]"
            >
              {{ project.name }} ({{ project.collections[0] }})
            </option>
          </select>
        </div>

        <!-- Topic Input -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">Topic / Query</label>
          <input
            v-model="topicQuery"
            type="text"
            placeholder="e.g., Introduction to Machine Learning"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500"
          />
          <p class="mt-1 text-xs text-gray-500">
            💡 The system will find relevant sections from your document
          </p>
        </div>

        <!-- Language & Voice -->
        <div class="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Language</label>
            <select
              v-model="genLanguage"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500"
            >
              <option value="en">🇺🇸 English</option>
              <option value="hi">🇮🇳 Hindi</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Voice</label>
            <select
              v-model="genVoice"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500"
            >
              <option value="">Default</option>
              <option value="en-US-GuyNeural">Guy (Male)</option>
              <option value="en-US-JennyNeural">Jenny (Female)</option>
              <option value="hi-IN-MadhurNeural">Madhur (Hindi Male)</option>
              <option value="hi-IN-SwaraNeural">Swara (Hindi Female)</option>
            </select>
          </div>
        </div>

        <!-- Generate Video Toggle -->
        <div class="mb-4 flex items-center">
          <input
            v-model="generateVideo"
            type="checkbox"
            id="gen-video"
            class="w-4 h-4 text-amber-600 border-gray-300 rounded focus:ring-amber-500"
          />
          <label for="gen-video" class="ml-2 text-sm text-gray-700">
            Generate video (slides + audio + subtitles)
          </label>
        </div>

        <!-- Generate Button -->
        <button
          @click="generatePresentation"
          :disabled="!selectedCollection || !topicQuery || generating"
          class="w-full py-3 px-6 rounded-lg font-semibold text-white transition-all transform hover:scale-105
                 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
          :class="generating ? 'bg-gray-400' : 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700'"
        >
          <span v-if="generating">
            <svg class="animate-spin inline-block w-5 h-5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Generating... This may take a few minutes
          </span>
          <span v-else>✨ Generate Presentation</span>
        </button>

        <!-- Generation Result -->
        <div v-if="generationResult" class="mt-6 p-4 rounded-lg bg-purple-50 border border-purple-200">
          <h4 class="font-semibold text-purple-900 mb-2">🎉 Generation Complete!</h4>
          <div class="text-sm text-purple-800 space-y-1">
            <p>📊 Slides: {{ generationResult.slide_count }}</p>
            <p>🎵 Duration: {{ generationResult.duration }}s</p>
            <p v-if="generationResult.rag_enabled">
              🧠 RAG: Retrieved {{ generationResult.chunks_retrieved }} relevant chunks
            </p>
            <p v-if="generationResult.video_path" class="text-green-700 font-medium mt-2">
              ✅ Video ready! Switch to Viewer tab to watch.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Viewer Tab -->
    <div v-if="activeTab === 'viewer'" class="animate-fade-in">
      <div class="glass-card rounded-xl p-6 shadow-lg backdrop-blur-xl">
        <h3 class="text-xl font-semibold text-amber-900 mb-4">📺 Video Viewer</h3>
        
        <!-- Project Selection -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">Select Project</label>
          <select
            v-model="viewerProject"
            @change="loadVideo"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500"
          >
            <option value="">Choose a project...</option>
            <option v-for="project in projects" :key="project.name" :value="project.name">
              {{ project.name }}
            </option>
          </select>
        </div>

        <!-- Video Player -->
        <div v-if="videoPath" class="mt-4">
          <div class="relative">
            <video
              ref="viewerVideoElement"
              :src="videoPath"
              controls
              class="w-full rounded-lg shadow-lg"
              style="max-height: 500px;"
            >
              Your browser does not support the video tag.
            </video>
          </div>
          
          <!-- Enhanced Controls -->
          <div class="mt-4 flex flex-wrap gap-3">
            <!-- Playback Speed -->
            <div class="flex items-center gap-2">
              <label class="text-sm font-medium text-gray-700">Speed:</label>
              <select
                v-model="playbackSpeed"
                @change="changePlaybackSpeed"
                class="px-3 py-1 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-amber-500"
              >
                <option :value="0.5">0.5x</option>
                <option :value="0.75">0.75x</option>
                <option :value="1">1x</option>
                <option :value="1.25">1.25x</option>
                <option :value="1.5">1.5x</option>
                <option :value="2">2x</option>
              </select>
            </div>
            
            <!-- Share Button -->
            <button
              @click="shareVideo"
              class="px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all shadow-md hover:shadow-lg flex items-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
              </svg>
              Share Lecture
            </button>
            
            <!-- Download Button -->
            <button
              @click="downloadVideo"
              class="px-4 py-2 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-lg hover:from-green-600 hover:to-green-700 transition-all shadow-md hover:shadow-lg flex items-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Download
            </button>
          </div>
        </div>
        <div v-else class="text-center py-12 text-gray-500">
          Select a project to view its video
        </div>
      </div>
      
      <!-- Share Modal -->
      <div v-if="showShareModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="showShareModal = false">
        <div class="bg-white rounded-xl p-6 max-w-md w-full mx-4 shadow-2xl">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-xl font-semibold text-gray-900">🔗 Share Lecture</h3>
            <button @click="showShareModal = false" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">Local File Path:</label>
            <div class="flex gap-2">
              <input
                :value="shareFilePath"
                readonly
                class="flex-1 px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg text-sm"
              />
              <button
                @click="copyToClipboard(shareFilePath)"
                class="px-3 py-2 bg-amber-500 text-white rounded-lg hover:bg-amber-600 transition-colors"
              >
                📋 Copy
              </button>
            </div>
            <p class="mt-2 text-xs text-gray-500">You can share this file via your preferred method (email, cloud storage, USB, etc.)</p>
          </div>
          
          <div class="border-t pt-4">
            <p class="text-sm text-gray-600 mb-3">
              <strong>Sharing Tips:</strong>
            </p>
            <ul class="text-sm text-gray-600 space-y-1 list-disc list-inside">
              <li>Upload to Google Drive, OneDrive, or Dropbox</li>
              <li>Share via email or messaging apps</li>
              <li>Host on your own web server</li>
              <li>Transfer via USB drive</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Interactive Lecture Tab -->
    <div v-if="activeTab === 'interactive'" class="animate-fade-in">
      <div class="glass-card rounded-xl p-6 shadow-lg backdrop-blur-xl">
        <h3 class="text-xl font-semibold text-amber-900 mb-4">🎭 Interactive Lecture Player</h3>
        
        <!-- Project Selection -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">Select Lecture</label>
          <select
            v-model="interactiveProject"
            @change="loadInteractiveLecture"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500"
          >
            <option value="">Choose a lecture...</option>
            <option v-for="project in projects" :key="project.name" :value="project.name">
              {{ project.name }}
            </option>
          </select>
        </div>

        <!-- Loading State -->
        <div v-if="loadingInteractive" class="text-center py-12">
          <svg class="animate-spin w-12 h-12 mx-auto text-amber-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p class="mt-4 text-gray-600">Loading interactive lecture...</p>
        </div>

        <!-- Error State -->
        <div v-if="interactiveError" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
          <p class="text-red-800">{{ interactiveError }}</p>
        </div>

        <!-- Interactive Lecture Player -->
        <InteractiveLecture
          v-if="interactiveAudioSrc && interactiveTimings && interactiveAnimations"
          :audioSrc="interactiveAudioSrc"
          :timings="interactiveTimings"
          :animations="interactiveAnimations"
          :projectName="selectedInteractiveProject"
        />
        
        <!-- Empty State -->
        <div v-else-if="!loadingInteractive" class="text-center py-12">
          <div class="text-6xl mb-4">🎬</div>
          <p class="text-gray-600 text-lg">Select a lecture to start the interactive experience</p>
          <p class="text-gray-500 text-sm mt-2">
            Enjoy AI-powered animations synced with narration!
          </p>
        </div>
      </div>
    </div>

    <!-- Study Mode Tab -->
    <div v-if="activeTab === 'study'" class="animate-fade-in">
      <InteractiveStudyMode :projects="projects" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { fetch as tauriFetch } from '@tauri-apps/api/http'
import { Body } from '@tauri-apps/api/http'
import { convertFileSrc } from '@tauri-apps/api/tauri'
import InteractiveStudyMode from './InteractiveStudyMode.vue'
import InteractiveLecture from './interactive/InteractiveLecture.vue'

const activeTab = ref('upload')
const projectName = ref('my-lecture')
const selectedFile = ref(null)
const uploading = ref(false)
const uploadResult = ref(null)
const uploadError = ref(null)
const projects = ref([])
const selectedCollection = ref('')
const topicQuery = ref('')
const genLanguage = ref('en')
const genVoice = ref('')
const generateVideo = ref(true)
const generating = ref(false)
const generationResult = ref(null)
const viewerProject = ref('')
const videoPath = ref(null)
const viewerVideoElement = ref(null)
const playbackSpeed = ref(1)
const showShareModal = ref(false)
const shareFilePath = ref('')

// Interactive Lecture Player state
const interactiveProject = ref('')
const interactiveAudioSrc = ref(null)
const interactiveTimings = ref(null)
const interactiveAnimations = ref(null)
const loadingInteractive = ref(false)
const interactiveError = ref(null)

onMounted(() => {
  loadProjects()
})

function handleFileSelect(event) {
  selectedFile.value = event.target.files[0]
  uploadResult.value = null
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

async function uploadDocument() {
  if (!selectedFile.value || !projectName.value) return
  
  uploading.value = true
  uploadResult.value = null
  uploadError.value = null
  
  try {
    console.log('🚀 Starting document upload...')
    console.log('   Project:', projectName.value)
    console.log('   File:', selectedFile.value.name)
    
    // Use standard fetch with FormData instead of Tauri fetch
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('project', projectName.value)
    
    console.log('📤 Uploading to backend...')
    
    // Use native fetch API which handles multipart correctly
    const response = await fetch('http://127.0.0.1:8765/upload_document', {
      method: 'POST',
      body: formData
    })
    
    console.log('📥 Response received:', response.status)
    
    if (response.ok) {
      const data = await response.json()
      uploadResult.value = data
      console.log('✅ Upload successful!')
      console.log('   Topics found:', data.topics?.length || 0)
      console.log('   Chunks created:', data.chunk_count)
      
      await loadProjects() // Refresh projects list
    } else {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
      const errorMsg = errorData.detail || 'Unknown error'
      uploadError.value = errorMsg
      console.error('❌ Upload failed:', errorMsg)
      alert('Upload failed: ' + errorMsg)
    }
  } catch (error) {
    console.error('❌ Upload error:', error)
    uploadError.value = error.message
    alert('Upload failed: ' + error.message)
  } finally {
    uploading.value = false
  }
}

async function loadProjects() {
  try {
    const response = await tauriFetch('http://127.0.0.1:8765/list_projects', {
      method: 'GET',
      responseType: 1
    })
    
    if (response.ok) {
      projects.value = response.data.projects || []
    }
  } catch (error) {
    console.error('Failed to load projects:', error)
  }
}

function selectProject(project) {
  projectName.value = project.name
  if (project.collections.length > 0) {
    selectedCollection.value = project.collections[0]
    activeTab.value = 'generate'
  }
}

async function generatePresentation() {
  if (!selectedCollection.value || !topicQuery.value) return
  
  generating.value = true
  generationResult.value = null
  
  try {
    const payload = {
      project: projectName.value,
      collection_name: selectedCollection.value,
      topic: topicQuery.value,
      lang: genLanguage.value,
      voice: genVoice.value || null,
      generate_video: generateVideo.value
    }
    
    const response = await tauriFetch('http://127.0.0.1:8765/generate_from_topic', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: Body.json(payload),
      responseType: 1,
      timeout: 300 // 5 minute timeout
    })
    
    if (response.ok) {
      generationResult.value = response.data
      await loadProjects() // Refresh to show new video
    } else {
      alert('Generation failed: ' + (response.data?.detail || 'Unknown error'))
    }
  } catch (error) {
    console.error('Generation error:', error)
    alert('Generation failed: ' + error.message)
  } finally {
    generating.value = false
  }
}

async function loadVideo() {
  if (!viewerProject.value) {
    videoPath.value = null
    return
  }
  
  try {
    // Get video path from backend API to ensure correct path
    const response = await tauriFetch(
      `http://127.0.0.1:8765/get_video?project=${encodeURIComponent(viewerProject.value)}`,
      { method: 'GET', responseType: 1 }
    )
    
    if (!response.ok || !response.data || !response.data.video_path) {
      console.error('Video not found')
      videoPath.value = null
      return
    }
    
    const fullPath = response.data.video_path
    videoPath.value = convertFileSrc(fullPath)
    shareFilePath.value = fullPath
    
    console.log('Loading video from:', fullPath)
    console.log('Converted path:', videoPath.value)
  } catch (error) {
    console.error('Failed to load video path:', error)
    videoPath.value = null
  }
}

function changePlaybackSpeed() {
  if (viewerVideoElement.value) {
    viewerVideoElement.value.playbackRate = playbackSpeed.value
    console.log('Playback speed changed to:', playbackSpeed.value)
  }
}

function shareVideo() {
  if (!viewerProject.value) {
    alert('Please select a project first')
    return
  }
  showShareModal.value = true
}

function downloadVideo() {
  if (!viewerProject.value) {
    alert('Please select a project first')
    return
  }
  
  // Open the folder containing the video
  const lecturesPath = window.navigator.platform.toLowerCase().includes('win')
    ? `C:\\Users\\${window.navigator.userAgent.match(/Windows NT [^;)]+/)?.[0] || 'user'}\\Lectures\\${viewerProject.value}`
    : `~/Lectures/${viewerProject.value}`
  
  alert(`Video is located at:\n${shareFilePath.value}\n\nYou can copy this file to share it.`)
}

async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text)
    alert('Path copied to clipboard!')
  } catch (error) {
    console.error('Failed to copy:', error)
    // Fallback for older browsers
    const textArea = document.createElement('textarea')
    textArea.value = text
    document.body.appendChild(textArea)
    textArea.select()
    try {
      document.execCommand('copy')
      alert('Path copied to clipboard!')
    } catch (err) {
      alert('Failed to copy. Please copy manually:\n' + text)
    }
    document.body.removeChild(textArea)
  }
}

async function loadInteractiveLecture() {
  if (!interactiveProject.value) {
    interactiveAudioSrc.value = null
    interactiveTimings.value = null
    interactiveAnimations.value = null
    return
  }
  
  loadingInteractive.value = true
  interactiveError.value = null
  
  try {
    console.log('=== Loading Interactive Lecture ===')
    console.log('Project:', interactiveProject.value)
    
    // Get audio path from API to ensure correct path
    const audioInfoResp = await tauriFetch(
      `http://127.0.0.1:8765/get_audio?project=${encodeURIComponent(interactiveProject.value)}`,
      { method: 'GET', responseType: 1 }
    )
    
    if (!audioInfoResp.ok || !audioInfoResp.data || !audioInfoResp.data.audio_path) {
      throw new Error('Audio file not found for this lecture')
    }
    
    const audioPath = audioInfoResp.data.audio_path
    console.log('Audio path:', audioPath)
    
    const audioSrc = convertFileSrc(audioPath)
    console.log('Converted audio src:', audioSrc)
    
    interactiveAudioSrc.value = audioSrc
    
    // Load timings
    console.log('Loading slide timings...')
    const timingsResp = await tauriFetch(
      `http://127.0.0.1:8765/get_slide_timings?project=${encodeURIComponent(interactiveProject.value)}`,
      { method: 'GET', responseType: 1 }
    )
    
    if (!timingsResp.ok) {
      throw new Error('Failed to load slide timings')
    }
    
    interactiveTimings.value = timingsResp.data
    console.log('✅ Timings loaded:', interactiveTimings.value)
    
    // Load animations
    console.log('Loading animations...')
    const animationsResp = await tauriFetch(
      `http://127.0.0.1:8765/get_animations?project=${encodeURIComponent(interactiveProject.value)}`,
      { method: 'GET', responseType: 1 }
    )
    
    if (!animationsResp.ok) {
      throw new Error('Animations not available for this lecture. Please regenerate it to get interactive features.')
    }
    
    interactiveAnimations.value = animationsResp.data
    console.log('✅ Animations loaded:', interactiveAnimations.value)
    
    console.log('=== Interactive Lecture Ready ===')
    console.log('Audio:', interactiveAudioSrc.value)
    console.log('Slides:', interactiveAnimations.value?.slides?.length || 0)
    
  } catch (error) {
    console.error('❌ Failed to load interactive lecture:', error)
    interactiveError.value = error.message || 'Failed to load interactive lecture'
    interactiveAudioSrc.value = null
    interactiveTimings.value = null
    interactiveAnimations.value = null
  } finally {
    loadingInteractive.value = false
  }
}
</script>

<style scoped>
/* Wood texture background - matching Generate Audio page */
.wood-texture {
  background: 
    linear-gradient(rgba(217, 119, 6, 0.05), rgba(194, 65, 12, 0.05)),
    repeating-linear-gradient(
      90deg,
      #d4a574 0px,
      #c89968 2px,
      #ba8c5d 4px,
      #d4a574 6px
    );
  background-size: 100% 100%, 6px 100%;
  position: relative;
  min-height: 500px;
}

.wood-texture::before {
  content: '';
  position: absolute;
  inset: 0;
  background: 
    radial-gradient(ellipse at 20% 30%, rgba(217, 119, 6, 0.08) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 70%, rgba(194, 65, 12, 0.08) 0%, transparent 50%);
  pointer-events: none;
  border-radius: 1rem;
}

/* Glassmorphism header - liquid glass effect */
.glass-header {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

/* Glassmorphism cards - liquid glass effect */
.glass-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

/* Glass project cards - liquid glass */
.glass-project-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  border: 2px solid rgba(255, 255, 255, 0.25);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.glass-project-card:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(217, 119, 6, 0.3);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

/* Glass button - liquid glass */
.glass-button-amber {
  background: rgba(251, 191, 36, 0.15);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  border: 1px solid rgba(251, 191, 36, 0.3);
  color: #78350f;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(251, 191, 36, 0.1);
}

.glass-button-amber:hover {
  background: rgba(251, 191, 36, 0.25);
  border-color: rgba(251, 191, 36, 0.4);
  box-shadow: 0 6px 16px rgba(251, 191, 36, 0.15);
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in {
  animation: fade-in 0.4s ease-out;
}
</style>
