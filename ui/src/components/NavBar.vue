<template>
  <nav class="bg-darkest-wood fixed top-0 left-0 right-0 z-50 shadow-lg">
    <div class="container mx-auto px-6 py-4">
      <div class="flex items-center justify-between">
        <div class="text-amber-100 font-bold text-2xl">
          LECTRA
        </div>
        <div class="flex space-x-6">
          <a
            v-for="item in navItems"
            :key="item.id"
            href="#"
            @click.prevent="$emit('navigate', item.id)"
            class="text-amber-100/90 hover:text-amber-50 transition-colors duration-200"
          >
            {{ item.label }}
          </a>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
const navItems = [
  { id: 'home', label: '🏠 Home' },
  { id: 'features', label: '✨ Features' },
  { id: 'tech', label: '🔧 Tech' },
  { id: 'generate', label: '🎤 Generate' },
  { id: 'notebook', label: '📚 Notebook' },
  { id: 'details', label: 'ℹ️ Details' },
]

defineEmits(['navigate'])
</script>
