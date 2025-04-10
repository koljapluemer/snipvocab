<template>
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <h2 class="card-title">Watch the Snippet</h2>
      <div class="max-w-full">
        <div class="mb-4 relative aspect-video">
          <iframe
            :key="replayKey"
            class="w-full h-full"
            :src="youtubeEmbedUrl"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen>
          </iframe>
        </div>
      </div>
      <div class="flex flex-col items-center space-y-4">
        <button @click="replaySnippet" class="btn btn-primary">
          Replay Snippet
        </button>
        <div class="btn-group gap-2">
          <button @click="onStudyAgain" class="btn btn-warning">
            Study Again
          </button>
          <router-link
            :to="{ name: 'snippet', params: { videoId: snippet.videoId, index: snippet.index + 1 }}"
            class="btn btn-success"
          >
            Next Snippet
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Snippet } from '@/shared/types/domainTypes'

const props = defineProps<{
  snippet: Snippet
}>()

const replayKey = ref(Date.now())

const youtubeEmbedUrl = computed(() => {
  const start = Math.floor(props.snippet.startTime)
  const end = Math.floor(props.snippet.endTime)
  // Added enablejsapi=1 to enable API control and rel=0 to prevent showing related videos
  return `https://www.youtube.com/embed/${props.snippet.videoId}?start=${start}&end=${end}&autoplay=1&enablejsapi=1&rel=0&version=3`
})

const replaySnippet = () => {
  // Update the replayKey to force iframe reload
  replayKey.value = Date.now()
}

const emit = defineEmits<{
  (e: 'study-again'): void
}>()

const onStudyAgain = () => {
  emit('study-again')
}
</script>
