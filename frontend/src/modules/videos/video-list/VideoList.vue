<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getVideos, type VideoInfo } from '@/modules/backend-communication/api'
import VideoTile from './VideoTile.vue'

const videos = ref<VideoInfo[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

const fetchVideos = async () => {
  loading.value = true
  error.value = null
  videos.value = await getVideos()
  loading.value = false
}

onMounted(() => {
  fetchVideos()
})
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-6">Select a video to practice:</h1>
    
    <div v-if="loading" class="flex justify-center">
      <span class="loading loading-spinner loading-lg"></span>
    </div>

    <div v-else-if="error" class="alert alert-error">
      <span>{{ error }}</span>
    </div>

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
      <VideoTile
        v-for="video in videos"
        :key="video.youtube_id"
        :video-id="video.youtube_id"
        :title="video.youtube_title"
      />
    </div>
  </div>
</template>
