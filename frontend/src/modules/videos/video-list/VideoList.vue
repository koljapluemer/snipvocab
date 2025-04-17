<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { 
  getVideos, 
  getVideosByTag,
  getNewestVideos,
  getPopularVideos,
} from '@/modules/backend-communication/api'
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'
import VideoTile from '@/modules/videos/video-list/VideoTile.vue'
import { DisplaySource } from './types'
import type { PaginatedResponse, VideoInfo } from '@/modules/backend-communication/apiTypes'

const props = defineProps<{
  source: DisplaySource
  tag?: string
}>()

// Each page from the backend corresponds to exactly one slide
const slides = ref<VideoInfo[][]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const currentPage = ref(1)
const hasMore = ref(true)
const isLoadingMore = ref(false)

const getFetchFunction = () => {
  switch (props.source) {
    case DisplaySource.ALL_VIDEOS:
      return getVideos
    case DisplaySource.VIDEOS_WITH_TAG:
      if (!props.tag) throw new Error('Tag is required for VIDEOS_WITH_TAG source')
      return (page: number) => getVideosByTag(props.tag!, page)
    case DisplaySource.NEWEST_VIDEOS:
      return getNewestVideos
    case DisplaySource.POPULAR_VIDEOS:
      return getPopularVideos
    default:
      throw new Error(`Unknown display source: ${props.source}`)
  }
}

const fetchVideos = async (page: number = 1) => {
  loading.value = true
  error.value = null
  
  try {
    const fetchFn = getFetchFunction()
    const response: PaginatedResponse<VideoInfo> = await fetchFn(page)
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
    const fetchFn = getFetchFunction()
    const response: PaginatedResponse<VideoInfo> = await fetchFn(nextPage)
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
    const fetchFn = getFetchFunction()
    const response: PaginatedResponse<VideoInfo> = await fetchFn(prevPage)
    slides.value[prevPage - 1] = response.results
    currentPage.value = prevPage
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to load previous videos'
  } finally {
    isLoadingMore.value = false
  }
}

// Reset and refetch when source or tag changes
watch([() => props.source, () => props.tag], () => {
  slides.value = []
  currentPage.value = 1
  hasMore.value = true
  fetchVideos()
})

onMounted(() => {
  fetchVideos()
})
</script>

<template>
  <div class="container mx-auto py-8">
    <h2 class="text-3xl font-bold text-primary mb-8 text-center">
      <template v-if="source === DisplaySource.ALL_VIDEOS">All Videos</template>
      <template v-else-if="source === DisplaySource.VIDEOS_WITH_TAG">{{ tag }}</template>
      <template v-else-if="source === DisplaySource.NEWEST_VIDEOS">Newly Added</template>
      <template v-else-if="source === DisplaySource.POPULAR_VIDEOS">Popular on YouTube</template>
    </h2>
    
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

