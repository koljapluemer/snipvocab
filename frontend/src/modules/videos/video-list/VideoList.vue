<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getVideos, type VideoInfo, type PaginatedResponse } from '@/modules/backend-communication/api'
import VideoTile from './VideoTile.vue'
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'

// Each page from the backend corresponds to exactly one slide
const slides = ref<VideoInfo[][]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const currentPage = ref(1)
const hasMore = ref(true)
const isLoadingMore = ref(false)

const fetchVideos = async (page: number = 1) => {
  loading.value = true
  error.value = null
  
  try {
    const response: PaginatedResponse<VideoInfo> = await getVideos(page)
    slides.value[page - 1] = response.results
    hasMore.value = !!response.next
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to fetch videos'
  } finally {
    loading.value = false
  }
}

const loadNextPage = async () => {
  if (!hasMore.value || isLoadingMore.value) return
  isLoadingMore.value = true
  try {
    const nextPage = currentPage.value + 1
    const response: PaginatedResponse<VideoInfo> = await getVideos(nextPage)
    slides.value[nextPage - 1] = response.results
    currentPage.value = nextPage
    hasMore.value = !!response.next
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to load more videos'
  } finally {
    isLoadingMore.value = false
  }
}

const loadPreviousPage = async () => {
  if (currentPage.value <= 1 || isLoadingMore.value) return
  isLoadingMore.value = true
  try {
    const prevPage = currentPage.value - 1
    const response: PaginatedResponse<VideoInfo> = await getVideos(prevPage)
    slides.value[prevPage - 1] = response.results
    currentPage.value = prevPage
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to load previous videos'
  } finally {
    isLoadingMore.value = false
  }
}

onMounted(() => {
  fetchVideos()
})
</script>

<template>
  <div class="container mx-auto py-8">
    <h2 class="text-2xl font-bold mb-6 ml-14">All Videos</h2>
    
    <div v-if="loading && !slides.length" class="flex justify-center">
      <span class="loading loading-spinner loading-lg"></span>
    </div>

    <div v-else-if="error" class="alert alert-error">
      <span>{{ error }}</span>
    </div>

    <div v-else class="flex items-center gap-4">
      <button 
        class="btn btn-circle"
        :class="{ 'btn-disabled': currentPage <= 1 }"
        @click="loadPreviousPage"
      >
        <ChevronLeft v-if="!isLoadingMore" class="w-6 h-6" />
        <span v-else class="loading loading-spinner loading-xs"></span>
      </button>

      <div class="flex-1 grid grid-cols-2 md:grid-cols-4 gap-4">
        <template v-if="slides[currentPage - 1]">
          <div 
            v-for="video in slides[currentPage - 1]" 
            :key="video.youtube_id"
            class="w-full"
          >
            <VideoTile
              :video-id="video.youtube_id"
              :title="video.youtube_title"
            />
          </div>
        </template>
        <template v-else>
          <div v-for="i in 4" :key="i" class="w-full">
            <div class="skeleton h-48 w-full"></div>
          </div>
        </template>
      </div>

      <button 
        class="btn btn-circle"
        :class="{ 'btn-disabled': !hasMore }"
        @click="loadNextPage"
      >
        <ChevronRight v-if="!isLoadingMore" class="w-6 h-6" />
        <span v-else class="loading loading-spinner loading-xs"></span>
      </button>
    </div>
  </div>
</template>

<style scoped>
@media (max-width: 640px) {
  .px-16 {
    padding-left: 2rem;
    padding-right: 2rem;
  }
}
</style>

