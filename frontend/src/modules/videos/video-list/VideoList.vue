<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getVideos } from '@/modules/backend-communication/api'
import VideoTile from './VideoTile.vue'

const videoIds = ref<string[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

const fetchVideos = async () => {
  loading.value = true
  error.value = null
  videoIds.value = await getVideos()
  loading.value = false
}

onMounted(() => {
  fetchVideos()
})
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-6">Egyptian Arabic Videos</h1>
    
    <div v-if="loading" class="flex justify-center">
      <span class="loading loading-spinner loading-lg"></span>
    </div>

    <div v-else-if="error" class="alert alert-error">
      <span>{{ error }}</span>
    </div>

    <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-2">
      <VideoTile
        v-for="videoId in videoIds"
        :key="videoId"
        :video-id="videoId"
      />
    </div>
  </div>
</template>
