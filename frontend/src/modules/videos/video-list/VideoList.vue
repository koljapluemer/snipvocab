<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getVideos } from '@/modules/backend-communication/api'

const videoIds = ref<string[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const router = useRouter()

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

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="videoId in videoIds" :key="videoId" class="card bg-base-100 shadow-xl">
        <figure class="px-4 pt-4">
          <img 
            :src="`https://img.youtube.com/vi/${videoId}/mqdefault.jpg`" 
            :alt="`Video thumbnail for ${videoId}`"
            class="rounded-xl"
          />
        </figure>
        <div class="card-body">
          <div class="card-actions justify-end mt-4">
            <button 
              class="btn btn-primary"
              @click="router.push({ name: 'video', params: { videoId }})"
            >
              View Video
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
