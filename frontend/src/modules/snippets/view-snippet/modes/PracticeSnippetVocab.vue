<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { Snippet, WordFlashCard } from '@/shared/types/domainTypes'
import { getSnippetDueWords } from '@/modules/backend-communication/api'

const props = defineProps<{
  snippet: Snippet
}>()

const dueWords = ref<WordFlashCard[]>([])
const isLoading = ref(false)
const error = ref<string | null>(null)

const fetchDueWords = async () => {
  try {
    isLoading.value = true
    error.value = null
    console.log('fetching due words for snippet', props.snippet)
    dueWords.value = await getSnippetDueWords(props.snippet.videoId, props.snippet.index)
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to fetch due words'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchDueWords()
})
</script>

<template>
  <div class="p-4">
    <h2 class="text-xl font-bold mb-4">Due Words</h2>
    
    <div v-if="isLoading" class="flex justify-center">
      <span class="loading loading-spinner loading-lg"></span>
    </div>
    
    <div v-else-if="error" class="alert alert-error">
      <span>{{ error }}</span>
    </div>
    
    <div v-else-if="dueWords.length === 0" class="alert alert-info">
      <span>No words are due for this snippet</span>
    </div>
    
    <div v-else class="space-y-2">
      <div v-for="word in dueWords" :key="word.original_word" class="card bg-base-100 shadow">
        <div class="card-body">
          <h3 class="card-title">{{ word.original_word }}</h3>
          <div class="space-y-1">
            <div v-for="meaning in word.meanings" :key="meaning.en" class="text-sm">
              {{ meaning.en }}
            </div>
          </div>
          <div class="flex gap-2 mt-2">
            <span v-if="word.isNew" class="badge badge-primary">New</span>
            <span v-if="word.isFavorite" class="badge badge-secondary">Favorite</span>
            <span v-if="word.isBlacklisted" class="badge badge-error">Blacklisted</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
