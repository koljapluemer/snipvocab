<script setup lang="ts">
import type { Snippet } from '@/shared/types/domainTypes'
import { ref, onMounted, watch } from 'vue'
import PracticeSnippetVocab from './modes/PracticeSnippetVocab.vue'
import WatchSnippet from './modes/WatchSnippet.vue';

const props = defineProps<{
  videoId: string
  index: string
  startTime: string
  endTime: string
}>()

const snippet: Snippet = {
  videoId: props.videoId,
  index: Number(props.index),
  startTime: Number(props.startTime),
  endTime: Number(props.endTime)
}

enum SnippetStatus {
  'LEARNING_VOCAB',
  'WATCHING_SNIPPET'
}

const status = ref<SnippetStatus>(SnippetStatus.LEARNING_VOCAB)

const onPracticeCompleted = () => {
  status.value = SnippetStatus.WATCHING_SNIPPET
}
</script>

<template>
  <div class="container mx-auto p-4">

    <router-link :to="{ name: 'video', params: { videoId: snippet.videoId } }" class="btn btn-primary">
      Back to Video
    </router-link>

    <PracticeSnippetVocab v-if="status === SnippetStatus.LEARNING_VOCAB" :snippet="snippet" @practice-completed="onPracticeCompleted" />
    <WatchSnippet v-if="status === SnippetStatus.WATCHING_SNIPPET" :snippet="snippet" />
  </div>
</template>
