<template>
  <div class="flex flex-wrap justify-center gap-4">
    <div
      v-for="tech in techStack"
      :key="tech"
      class="glass-card px-6 py-3 font-bold hover:bg-white/95 transition-colors duration-200"
      style="color: #f5deb3;"
    >
      {{ tech }}
    </div>
  </div>
</template>

<script setup>
const techStack = [
  'Python',
  'FastAPI',
  'EdgeTTS',
  'FFmpeg',
  'Ollama',
  'Llama-3.1',
  'PostgreSQL',
  'Vue 3',
  'Tailwind CSS',
  'Tauri',
  'Rust'
]
</script>
