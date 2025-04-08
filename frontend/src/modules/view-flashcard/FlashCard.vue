<template>
  <div class="card shadow-lg p-4 mb-4">
    <div>
      <p class="text-4xl font-bold mb-2">{{ flashcard.original_word }}</p>
    </div>
    <!-- Display meanings -->
    <div v-if="revealed" class="mt-4">
      <ul>
        <li v-for="(meaning, index) in flashcard.meanings" :key="index"
            class="odd:bg-gray-500 even:bg-gray-600 p-2">
          <p class="text-lg">{{ meaning }}</p>
        </li>
      </ul>
    </div>
    <div v-else class="mt-4">
      <button class="btn btn-primary" @click="reveal">Reveal</button>
    </div>
    <div v-if="revealed" class="mt-4">
      <div class="btn-group flex flex-row gap-2">
        <button class="btn btn-warning" @click="rate(Rating.Again)">Again</button>
        <button class="btn btn-secondary" @click="rate(Rating.Hard)">Hard</button>
        <button class="btn btn-success" @click="rate(Rating.Good)">Good</button>
        <button class="btn btn-accent" @click="rate(Rating.Easy)">Easy</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { Flashcard } from '@/shared/types/domainTypes'
import { Rating } from 'ts-fsrs'

const props = defineProps<{
  flashcard: Flashcard
}>()

const emit = defineEmits<{
  (e: 'single-flashcard-rated', rating: Rating): void
}>()

const revealed = ref(false)

// Reset revealed state when flashcard changes
watch(() => props.flashcard, () => {
  revealed.value = false
})

const reveal = () => {
  revealed.value = true
}

const rate = (rating: Rating) => {
  emit('single-flashcard-rated', rating)
}
</script>
