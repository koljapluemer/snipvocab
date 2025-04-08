<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api, handleApiResponse } from '@/modules/backend-communication/api'

interface Video {
  id: number
  youtube_id: string
  only_premium: boolean
  is_blacklisted: boolean
}

const videos = ref<Video[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const router = useRouter()

const fetchVideos = async () => {
  try {
    loading.value = true
    videos.value = await handleApiResponse<Video[]>(api.get('/learn/videos/arz/'))
  } catch (err) {
    console.error('Error fetching videos:', err)
    error.value = err instanceof Error ? err.message : 'An error occurred'
  } finally {
    loading.value = false
  }
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

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="video in videos" :key="video.id" class="card bg-base-100 shadow-xl">
        <figure class="px-4 pt-4">
          <img 
            :src="`https://img.youtube.com/vi/${video.youtube_id}/mqdefault.jpg`" 
            :alt="`Video thumbnail for ${video.youtube_id}`"
            class="rounded-xl"
          />
        </figure>
        <div class="card-body">
          <div class="flex items-center gap-2">
            <span v-if="video.only_premium" class="badge badge-primary">Premium</span>
            <span v-if="video.is_blacklisted" class="badge badge-error">Blacklisted</span>
          </div>
          <div class="card-actions justify-end mt-4">
            <button 
              class="btn btn-primary"
              @click="router.push({ name: 'video', params: { videoId: video.youtube_id }})"
            >
              View Video
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
