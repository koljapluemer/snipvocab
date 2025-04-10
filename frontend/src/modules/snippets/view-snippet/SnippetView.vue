<script setup lang="ts">
import type { Snippet } from '@/shared/types/domainTypes'
import { ref, onMounted, watch } from 'vue'
import PracticeSnippetVocab from './modes/PracticeSnippetVocab.vue'

const props = defineProps<{
  videoId: string
  index: string
  startTime: string
  endTime: string
}>()

// Debug the raw props
console.log('Raw props:', {
  videoId: props.videoId,
  index: props.index,
  startTime: props.startTime,
  endTime: props.endTime
})

const snippet: Snippet = {
  videoId: props.videoId,
  index: Number(props.index),
  startTime: Number(props.startTime),
  endTime: Number(props.endTime)
}

// Debug the parsed snippet
console.log('Parsed snippet:', snippet)

// Validate the numbers
if (isNaN(snippet.index) || isNaN(snippet.startTime) || isNaN(snippet.endTime)) {
  throw new Error('Route parameters must be valid numbers')
}

enum SnippetStatus {
  'LEARNING_VOCAB',
  'WATCHING_SNIPPET'
}

const status = ref<SnippetStatus>(SnippetStatus.LEARNING_VOCAB)
</script>

<template>
  <div class="container mx-auto p-4">
    <div class="bg-base-200 p-4 rounded-lg mb-4">
      <h3 class="font-bold mb-2">Debug Info:</h3>
      <pre>Raw props: {{ JSON.stringify({ videoId, index, startTime, endTime }, null, 2) }}</pre>
      <pre>Parsed snippet: {{ JSON.stringify(snippet, null, 2) }}</pre>
    </div>
    
    <router-link :to="{ name: 'video', params: { videoId: snippet.videoId } }" class="btn btn-primary">
      Back to Video
    </router-link>

    <PracticeSnippetVocab v-if="status === SnippetStatus.LEARNING_VOCAB" :snippet="snippet" />
    <WatchSnippet v-if="status === SnippetStatus.WATCHING_SNIPPET" :snippet="snippet" />
  </div>
</template>
