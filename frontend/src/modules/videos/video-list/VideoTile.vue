<script setup lang="ts">
import { useRouter } from 'vue-router'

const props = defineProps<{
  videoId: string
}>()

const router = useRouter()

const handleViewVideo = () => {
  router.push({ name: 'video', params: { videoId: props.videoId }})
}
</script>

<template>
  <div class="group relative cursor-pointer max-w-[240px] mx-auto" @click="handleViewVideo">
    <div class="relative overflow-hidden rounded-lg">
      <img 
        :src="`https://img.youtube.com/vi/${videoId}/mqdefault.jpg`" 
        :alt="`Video thumbnail for ${videoId}`"
        class="w-full transition-transform duration-300 group-hover:scale-105"
      />
      <div class="absolute inset-0 bg-black/20 group-hover:bg-black/30 transition-colors duration-300" />
    </div>
  </div>
</template>
