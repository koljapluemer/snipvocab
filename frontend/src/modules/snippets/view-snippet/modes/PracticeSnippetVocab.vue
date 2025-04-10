<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { Snippet, WordFlashCard } from '@/shared/types/domainTypes'
import { getSnippetDueWords } from '@/modules/backend-communication/api'

const props = defineProps<{
  snippet: Snippet
}>()

const emit = defineEmits<{
  (e: 'practice-completed'): void
}>()

const dueWords = ref<WordFlashCard[]>([])
const isLoading = ref(true)
const error = ref<string | null>(null)

// Current practice state
const currentIndex = ref(-1)
const isRevealed = ref(false)
const shuffledWords = ref<WordFlashCard[]>([])

const fetchDueWords = async () => {
  try {
    isLoading.value = true
    error.value = null
    dueWords.value = await getSnippetDueWords(props.snippet.videoId, props.snippet.index)
    console.log('dueWords', dueWords.value)
    // Shuffle the words
    shuffledWords.value = [...dueWords.value].sort(() => Math.random() - 0.5)
    if (shuffledWords.value.length > 0) {
      currentIndex.value = 0
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to fetch due words'
  } finally {
    isLoading.value = false
  }
}

const reveal = () => {
  isRevealed.value = true
}

const nextCard = () => {
  if (currentIndex.value < shuffledWords.value.length - 1) {
    currentIndex.value++
    isRevealed.value = false
  } else {
    // We've gone through all cards
    emit('practice-completed')
  }
}

onMounted(() => {
  fetchDueWords()
})
</script>

<template>
  <div class="container mx-auto p-4">
    <div v-if="isLoading" class="flex justify-center">
      <span class="loading loading-spinner loading-lg"></span>
    </div>

    <div v-else-if="error" class="alert alert-error">
      {{ error }}
    </div>

    <div v-else-if="shuffledWords.length === 0" class="alert alert-info">
      No words to practice in this snippet.
    </div>

    <div v-else-if="currentIndex >= 0" class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <!-- Word -->
        <h2 class="card-title text-4xl">
          {{ shuffledWords[currentIndex].originalWord }}
        </h2>

        <!-- Meanings (hidden until revealed) -->
        <div v-if="isRevealed" class="mt-4 space-y-2">
          <div v-for="meaning in shuffledWords[currentIndex].meanings" 
               :key="meaning.en"
               class="p-2 bg-base-200 rounded">
            {{ meaning.en }}
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="card-actions justify-end mt-4">
          <button v-if="!isRevealed" 
                  @click="reveal" 
                  class="btn btn-primary">
            Reveal
          </button>
          <div v-else class="flex gap-2">
            <button @click="nextCard" class="btn btn-error">Again</button>
            <button @click="nextCard" class="btn btn-warning">Hard</button>
            <button @click="nextCard" class="btn btn-success">Good</button>
            <button @click="nextCard" class="btn btn-accent">Easy</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
