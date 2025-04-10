<script setup lang="ts">
import type { Snippet } from '@/shared/types/domainTypes'
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import PracticeSnippetVocab from './modes/PracticeSnippetVocab.vue'
import WatchSnippet from './modes/WatchSnippet.vue';

enum SnippetStatus {
  'LEARNING_VOCAB',
  'WATCHING_SNIPPET'
}

const route = useRoute()
const status = ref<SnippetStatus>(SnippetStatus.LEARNING_VOCAB)

const createSnippet = (params: typeof route.params): Snippet => ({
  videoId: params.videoId as string,
  index: Number(params.index),
  startTime: Number(params.startTime),
  endTime: Number(params.endTime)
})

const snippet = ref<Snippet>(createSnippet(route.params))

// Watch for route changes
watch(
  () => route.params,
  (newParams) => {
    snippet.value = createSnippet(newParams)
    status.value = SnippetStatus.LEARNING_VOCAB
  }
)

const onPracticeCompleted = () => {
  status.value = SnippetStatus.WATCHING_SNIPPET
}
</script>

<template>
  <div class="container mx-auto p-4">
    <router-link :to="{ name: 'video', params: { videoId: snippet.videoId } }" class="btn btn-primary">
      Back to Video
    </router-link>

    <PracticeSnippetVocab 
      v-if="status === SnippetStatus.LEARNING_VOCAB" 
      :snippet="snippet" 
      @practice-completed="onPracticeCompleted" 
    />
    <WatchSnippet 
      v-if="status === SnippetStatus.WATCHING_SNIPPET" 
      :snippet="snippet"
      @study-again="status = SnippetStatus.LEARNING_VOCAB"
    />
  </div>
</template>
