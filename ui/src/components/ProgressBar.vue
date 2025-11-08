<template>
  <div class="w-full bg-blue-100 rounded-lg overflow-hidden">
    <div 
      class="bg-blue-600 h-2 transition-all duration-300 ease-out"
      :style="{ width: progress + '%' }"
    ></div>
    <p class="text-center text-sm text-red-950 font-medium py-2">{{ message }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

defineProps({
  message: String
})

const progress = ref(0)

onMounted(() => {
  // Fake progress animation
  const interval = setInterval(() => {
    if (progress.value < 90) {
      progress.value += Math.random() * 15
    }
  }, 500)

  // Cleanup
  return () => clearInterval(interval)
})
</script>
