<template>
  <div class="text-center animate-slide-up">
    <!-- Logo Image with fallback to text -->
    <div class="mb-8">
      <img 
        src="../assets/images/title.png" 
        alt="LECTRA" 
        class="mx-auto max-h-56 w-auto drop-shadow-[0_4px_12px_rgba(0,0,0,0.8)]"
        @error="imageError = true"
        v-if="!imageError"
        style="filter: drop-shadow(0 0 20px rgba(0,0,0,0.9)) drop-shadow(0 4px 8px rgba(0,0,0,0.8));"
      />
      <h1 v-else class="text-9xl font-black tracking-wider" style="color: #f5deb3; text-shadow: 0 0 20px rgba(0,0,0,0.9), 0 4px 8px rgba(0,0,0,0.8);">LECTRA</h1>
    </div>
    
    <div class="text-4xl mb-12 font-bold" style="color: #f5deb3; text-shadow: 0 2px 8px rgba(0,0,0,0.9), 0 0 15px rgba(0,0,0,0.7);">
      Lecture TTS with Realistic Audio
    </div>
    
    <!-- Tagline -->
    <p class="text-2xl font-semibold mb-20 max-w-4xl mx-auto px-4" style="color: #f5deb3; text-shadow: 0 2px 6px rgba(0,0,0,0.9), 0 0 12px rgba(0,0,0,0.6);">
      Generate natural, expressive speech from text using AI-powered nuance tagging
    </p>
    
    <!-- CTA Buttons -->
    <div class="flex flex-col sm:flex-row gap-6 justify-center px-4">
      <button
        @click="$emit('generate', 'en')"
        class="glass-card-90 px-12 py-6 text-2xl font-bold hover:bg-white/95 transition-all duration-300 transform hover:scale-105 shadow-2xl"
        style="color: #f5deb3;"
      >
        🎙️ Generate (English)
      </button>
      <button
        @click="$emit('generate', 'hi')"
        class="glass-card-90 px-12 py-6 text-2xl font-bold hover:bg-white/95 transition-all duration-300 transform hover:scale-105 shadow-2xl"
        style="color: #f5deb3;"
      >
        🎙️ Generate (हिंदी)
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineEmits(['generate'])
const imageError = ref(false)
</script>
