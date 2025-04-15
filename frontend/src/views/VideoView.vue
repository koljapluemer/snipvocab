<template>
  <div class="container mx-auto px-4 py-8">
    <div v-if="loading" class="text-center">
      <span class="loading loading-spinner loading-lg"></span>
    </div>
    <div v-else-if="error" class="alert alert-error">
      <span>{{ error }}</span>
    </div>
    <div v-else>
      <h1 class="text-3xl font-bold mb-6">{{ title }}</h1>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="aspect-w-16 aspect-h-9">
          <iframe
            :src="`https://www.youtube.com/embed/${videoId}`"
            class="w-full h-full"
            allowfullscreen
          ></iframe>
        </div>
        <div class="space-y-4">
          <h2 class="text-2xl font-semibold">Snippets</h2>
          <div v-if="snippets.length === 0" class="text-gray-500">
            No snippets available for this video.
          </div>
          <div v-else class="space-y-4">
            <div
              v-for="snippet in snippets"
              :key="snippet.index"
              class="card bg-base-100 shadow-xl"
            >
              <div class="card-body">
                <div class="flex justify-between items-center">
                  <div>
                    <span class="text-sm text-gray-500">
                      {{ formatTime(snippet.startTime) }} - {{ formatTime(snippet.endTime) }}
                    </span>
                    <div v-if="snippet.perceivedDifficulty !== null" class="mt-2">
                      <span class="text-sm">Difficulty: {{ snippet.perceivedDifficulty }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import type { EnrichedSnippetDetails } from '@/shared/types/domainTypes'
import { getVideoEnrichedSnippets, type EnrichedSnippetsResponse } from '@/modules/backend-communication/api'

const route = useRoute()
const videoId = route.params.videoId as string

const loading = ref(true)
const error = ref<string | null>(null)
const snippets = ref<EnrichedSnippetDetails[]>([])
const title = ref('')

const formatTime = (seconds: number): string => {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = Math.floor(seconds % 60)
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

onMounted(async () => {
  try {
    const response = await getVideoEnrichedSnippets(videoId)
    snippets.value = response.snippets
    title.value = response.title
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'An error occurred'
  } finally {
    loading.value = false
  }
})
</script> 