<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import type { Snippet, Word } from '@/shared/types/domainTypes'
import { getVideoSnippets, getSnippetDetails } from '@/modules/backend-communication/api'
import WatchSnippet from './WatchSnippet.vue'

const route = useRoute()

const snippet = ref<Snippet | null>(null)
const words = ref<Word[]>([])
const isLearnMode = ref(true)
const isLoading = ref(true)
const videoId = ref(route.params.videoId as string)
const snippetIndex = ref(parseInt(route.params.index as string))
const coverSubtitles = ref(false)

// Function to load snippet and words data
const loadData = async () => {
  try {
    isLoading.value = true
    isLearnMode.value = true
    console.info('Loading snippet and words for:', { 
      videoId: videoId.value, 
      snippetIndex: snippetIndex.value 
    })
    
    // Clear existing data while loading
    snippet.value = null
    words.value = []
    
    const snippetDetails = await getSnippetDetails(videoId.value, snippetIndex.value)
    snippet.value = {
      start_time: snippetDetails.start_time,
      end_time: snippetDetails.end_time,
      video_id: snippetDetails.video_id,
      index: snippetDetails.index
    }
    words.value = snippetDetails.words
    console.info('Data loaded successfully')
  } catch (error) {
    console.error('Failed to load snippet:', error)
  } finally {
    isLoading.value = false
  }
}

// Single source of truth for data loading
watch(
  () => ({ 
    videoId: route.params.videoId, 
    index: route.params.index 
  }),
  async (newParams) => {
    if (newParams.videoId && newParams.index) {
      videoId.value = newParams.videoId as string
      snippetIndex.value = parseInt(newParams.index as string)
      await loadData()
    }
  },
  { immediate: true }
)

onMounted(async () => {
  await loadData()
})

const handleAllWordsCompleted = () => {
  isLearnMode.value = false
}

const handleSingleWordRated = (word: Word, rating: number) => {
  // TODO: Update word state in database
  console.log('Word rated:', word, rating)
}
</script>

<template>
  <div class="container mx-auto p-4">
    <div v-if="snippet" class="space-y-4">
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title">Snippet Details</h2>
          <div class="space-y-2">
            <p><span class="font-semibold">Start Time:</span> {{ snippet.start_time }}s</p>
            <p><span class="font-semibold">End Time:</span> {{ snippet.end_time }}s</p>
            <p><span class="font-semibold">Snippet Index:</span> {{ snippetIndex }}</p>
          </div>
          <div class="card-actions justify-end mt-4">
            <router-link
              :to="{ name: 'video', params: { videoId } }"
              class="btn btn-primary"
            >
              Back to Video
            </router-link>
          </div>
        </div>
      </div>

      <div v-if="isLearnMode && !isLoading">
        <div class="space-y-4">
          <div v-for="word in words" :key="word.original_word" class="card bg-base-100 shadow-xl">
            <div class="card-body">
              <h3 class="card-title">{{ word.original_word }}</h3>
              <div class="space-y-2">
                <div v-for="meaning in word.meanings" :key="meaning.en" class="p-2 bg-base-200 rounded">
                  <p>{{ meaning.en }}</p>
                </div>
              </div>
              <div class="card-actions justify-end mt-4">
                <button class="btn btn-primary" @click="handleSingleWordRated(word, 1)">
                  Mark as Learned
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <WatchSnippet
        v-else-if="!isLoading"
        :video-id="videoId"
        :start="snippet.start_time"
        :duration="snippet.end_time - snippet.start_time"
        :current-index="snippetIndex"
        :cover-subtitles="coverSubtitles"
        @study-again="isLearnMode = true"
      />
    </div>
    <div v-else class="flex justify-center items-center h-64">
      <span class="loading loading-spinner loading-lg"></span>
    </div>
  </div>
</template>
