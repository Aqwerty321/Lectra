<template>
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
    <div
        v-for="feature in features"
        :key="feature.title"
        class="glass-card p-8 hover:shadow-2xl transition-shadow duration-300 animate-fade-in"
    >
        <div class="text-5xl mb-5">{{ feature.icon }}</div>
        <h3 class="text-2xl font-bold mb-3" style="color: #5C4033;">{{ feature.title }}</h3>
        <p class="font-medium text-base" style="color: #6F4E37;">{{ feature.description }}</p>
    </div>
</div>
</template>

<script setup>
const features = [
  {
    icon: '🎯',
    title: 'Nuance Tags',
    description: 'AI automatically adds prosody tags for natural rate, pitch, and pause variations.'
  },
  {
    icon: '🎭',
    title: 'Multivoice',
    description: 'Switch between voices per segment. Support for English, Hindi, and more languages.'
  },
  {
    icon: '🌍',
    title: 'Multilingual',
    description: 'English and Hindi built-in. EdgeTTS supports 100+ voices across languages.'
  },
  {
    icon: '⏱️',
    title: 'Deterministic Timing',
    description: 'Per-sentence start/end times calculated without analyzing audio waveforms.'
  },
  {
    icon: '📴',
    title: 'Offline-Ready',
    description: 'TTS works without internet after voice download. LLM runs locally via Ollama.'
  },
  {
    icon: '📊',
    title: 'PPT Sync',
    description: 'Optional PowerPoint bullet-to-audio cue mapping for presentation narration.'
  }
]
</script>
