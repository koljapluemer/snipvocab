<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { FlashCardStack, LearningEvent, Snippet, WordFlashCard } from '@/shared/types/domainTypes'
import { LearningEventType } from '@/shared/types/domainTypes'
import { getSnippetDueWords, getSnippetAllWords, sendLearningEvents } from '@/modules/backend-communication/api'
import { shuffleArray } from '@/shared/utils/listUtils';
import { useToast } from '@/shared/composables/useToast';
import { addFlashcardToEndOfStack, shuffleFlashcardIntoStack } from '@/modules/learning-and-spaced-repetition/cardStackUtils';

const props = defineProps<{
  snippet: Snippet
  loadAllWords?: boolean
}>()

const emit = defineEmits<{
  (e: 'practice-completed'): void
}>()

const toast = useToast();

const cardStack = ref<FlashCardStack>([])
const isLoading = ref(true)
const error = ref<string | null>(null)
const learningEvents = ref<LearningEvent[]>([])

// Current practice state
const currentCard = ref<WordFlashCard | null>(null)
const isRevealed = ref(false)

const fetchDueWords = async () => {
  try {
    isLoading.value = true
    error.value = null
    cardStack.value = props.loadAllWords 
      ? await getSnippetAllWords(props.snippet.videoId, props.snippet.index)
      : await getSnippetDueWords(props.snippet.videoId, props.snippet.index)
    console.log('dueWords', cardStack.value)
    // Shuffle the words
    cardStack.value = shuffleArray(cardStack.value)
    if (cardStack.value.length > 0) {
      currentCard.value = cardStack.value[0]
    } else {
      toast.info('No words to practice right now')
      emit('practice-completed')
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
  // remove first card from the array:  
  console.log('nextCard(): stack before', cardStack.value)
  cardStack.value.shift()
  console.log('nextCard(): stack after', cardStack.value)
  if (cardStack.value.length > 0) {
    currentCard.value = cardStack.value[0]
    isRevealed.value = false
  } else {
    // We've gone through all cards
    console.log('sending learning events', learningEvents.value)
    sendLearningEvents(learningEvents.value)
    emit('practice-completed')
  }
}

const scoreCurrentCard = (eventType: LearningEventType) => {
  learningEvents.value.push({
    eventType,
    timestamp: Date.now(),
    originalWord: currentCard.value!.originalWord
  })

  if (currentCard.value!.isNew) {
    currentCard.value!.isNew = false
    if (eventType === LearningEventType.HARD) {
      cardStack.value = shuffleFlashcardIntoStack(cardStack.value, currentCard.value!)
    }
    else if (eventType === LearningEventType.GOOD) {
      cardStack.value = addFlashcardToEndOfStack(cardStack.value, currentCard.value!)
    }
  } else {
    if (eventType === LearningEventType.AGAIN) {
      cardStack.value = shuffleFlashcardIntoStack(cardStack.value, currentCard.value!)
    } else if (eventType === LearningEventType.HARD) {
      cardStack.value = addFlashcardToEndOfStack(cardStack.value, currentCard.value!)
    }
  }

  nextCard()
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

    <div v-else-if="currentCard" class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <!-- Word -->
        <h2 class="card-title text-4xl">
          {{ currentCard.originalWord }}
        </h2>

        <!-- Meanings (hidden until revealed) -->
        <div v-if="isRevealed || currentCard.isNew" class="mt-4 space-y-2">
          <div v-for="meaning in currentCard.meanings" :key="meaning.en" class="p-2 bg-base-200 rounded">
            {{ meaning.en }}
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="card-actions  mt-4">
          <div class="flex gap-2" v-if="currentCard.isNew">
            <button @click="scoreCurrentCard(LearningEventType.HARD)" class="btn btn-warning">Seems Hard</button>
            <button @click="scoreCurrentCard(LearningEventType.GOOD)" class="btn btn-success">Seems Easy</button>
          </div>
          <div class="flex gap-2" v-else>
            <button v-if="!isRevealed" @click="reveal" class="btn btn-primary">
              Reveal
            </button>
            <div v-else class="flex gap-2">
              <button @click="scoreCurrentCard(LearningEventType.AGAIN)" class="btn btn-error">Again</button>
              <button @click="scoreCurrentCard(LearningEventType.HARD)" class="btn btn-warning">Hard</button>
              <button @click="scoreCurrentCard(LearningEventType.GOOD)" class="btn btn-success">Good</button>
              <button @click="scoreCurrentCard(LearningEventType.EASY)" class="btn btn-accent">Easy</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
