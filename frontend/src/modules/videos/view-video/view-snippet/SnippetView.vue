<script setup lang="ts">
import type { Snippet } from '@/shared/types/domainTypes'
import { ref, watch } from 'vue'
import PracticeSnippetVocab from './modes/PracticeSnippetVocab.vue'
import WatchSnippet from './modes/WatchSnippet.vue';

enum SnippetStatus {
  'LEARNING_VOCAB',
  'WATCHING_SNIPPET'
}

const props = defineProps<{
  snippet: Snippet
}>()

const status = ref<SnippetStatus>(SnippetStatus.LEARNING_VOCAB)
const loadAllWords = ref(false)

// Reset to LEARNING_VOCAB mode whenever snippet changes
watch(() => props.snippet, () => {
  status.value = SnippetStatus.LEARNING_VOCAB
  loadAllWords.value = false
})

const emit = defineEmits<{
  (e: 'next-snippet'): void
  (e: 'back-to-video'): void
}>()

const onPracticeCompleted = () => {
  status.value = SnippetStatus.WATCHING_SNIPPET
}

const onNextSnippet = () => {
  emit('next-snippet')
}

const onPracticeAllWords = () => {
  loadAllWords.value = true
  status.value = SnippetStatus.LEARNING_VOCAB
}
</script>

<template>
  <div class="container mx-auto p-4">
    <button @click="emit('back-to-video')" class="btn btn-primary mb-4">
      Back to Video
    </button>

    <PracticeSnippetVocab 
      v-if="status === SnippetStatus.LEARNING_VOCAB" 
      :snippet="snippet" 
      :load-all-words="loadAllWords"
      @practice-completed="onPracticeCompleted" 
    />
    <WatchSnippet 
      v-if="status === SnippetStatus.WATCHING_SNIPPET" 
      :snippet="snippet"
      @study-again="status = SnippetStatus.LEARNING_VOCAB"
      @practice-all-words="onPracticeAllWords"
      @next-snippet="onNextSnippet"
    />
  </div>
</template>
