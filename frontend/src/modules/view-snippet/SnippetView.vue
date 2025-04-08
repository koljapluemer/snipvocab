<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import type { Snippet, Flashcard } from '@/shared/types/domainTypes'
import { getVideoSnippets, getSnippetWords } from '@/modules/videos/videoApi'
import FlashCardsWrapper from '@/modules/view-flashcard/FlashCardsWrapper.vue'
import WatchSnippet from './WatchSnippet.vue'
import { createEmptyCard, type Card } from 'ts-fsrs'

const route = useRoute()

const snippet = ref<Snippet | null>(null)
const flashcards = ref<Flashcard[]>([])
const isLearnMode = ref(true)
const isLoading = ref(true)
const videoId = route.params.videoId as string
const snippetIndex = parseInt(route.params.index as string)
const coverSubtitles = ref(false)

// Helper function to get snippet by index
const getSnippetByIndex = async (youtubeId: string, index: number): Promise<Snippet> => {
  const snippets = await getVideoSnippets(youtubeId)
  const snippet = snippets.find((s: Snippet) => s.index === index)
  if (!snippet) {
    throw new Error(`Snippet with index ${index} not found`)
  }
  return snippet
}

// Helper function to get flashcards for a snippet
const getFlashcardsForSnippet = async (youtubeId: string, snippetIndex: number): Promise<Flashcard[]> => {
  const words = await getSnippetWords(youtubeId, snippetIndex)
  const cards: Flashcard[] = []
  for (const word of words) {
    const card: Card = createEmptyCard()
    cards.push({
      ...card,
      original_word: word.original_word,
      meanings: word.meanings,
    })
  }
  return cards
}

onMounted(async () => {
  try {
    console.info('Loading snippet and flashcards for:', { videoId, snippetIndex })
    snippet.value = await getSnippetByIndex(videoId, snippetIndex)
    console.info('Snippet loaded:', snippet.value)
    flashcards.value = await getFlashcardsForSnippet(videoId, snippetIndex)
    console.info('Flashcards loaded:', flashcards.value)
    isLearnMode.value = true
    isLoading.value = false
  } catch (error) {
    console.error('Failed to load snippet:', error)
    isLoading.value = false
  }
})

const handleAllFlashcardsCompleted = () => {
  isLearnMode.value = false
}

const handleSingleFlashcardRated = (flashcard: Flashcard, rating: number) => {
  // TODO: Update flashcard state in database
  console.log('Flashcard rated:', flashcard, rating)
}
</script>

<template>
  <div class="container mx-auto p-4">
    <div v-if="snippet" class="space-y-4">
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title">Snippet Details</h2>
          <div class="space-y-2">
            <p><span class="font-semibold">Start Time:</span> {{ snippet.start }}s</p>
            <p><span class="font-semibold">Duration:</span> {{ snippet.duration }}s</p>
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
        <FlashCardsWrapper
          :flashcards="flashcards"
          @single-flashcard-rated="handleSingleFlashcardRated"
          @all-flashcards-completed="handleAllFlashcardsCompleted"
        />
      </div>
      <WatchSnippet
        v-else-if="!isLoading"
        :video-id="videoId"
        :start="snippet.start"
        :duration="snippet.duration"
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
