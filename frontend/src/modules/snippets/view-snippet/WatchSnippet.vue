<template>
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <h2 class="card-title">Watch the Snippet</h2>
      <div class="max-w-full">
        <div class="mb-4 relative aspect-video">
          <iframe
            class="w-full h-full"
            :src="youtubeEmbedUrl"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen>
          </iframe>
          <div v-if="coverSubtitles" class="absolute bottom-6 left-0 right-0 h-32 bg-gray-800"></div>
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
            :to="{ name: 'snippet', params: { videoId, index: currentIndex + 1 }}"
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

const props = defineProps<{
  videoId: string
  start: number
  duration: number
  currentIndex: number
  coverSubtitles: boolean
}>()

const replayKey = ref(Date.now())

const youtubeEmbedUrl = computed(() => {
  const start = Math.floor(props.start)
  const end = Math.floor(props.start + props.duration + 0.6)
  return `https://www.youtube.com/embed/${props.videoId}?start=${start}&end=${end}&autoplay=1`
})

const replaySnippet = () => {
  replayKey.value = Date.now()
}

const onStudyAgain = () => {
  // Emit event to parent to switch back to learn mode
  emit('study-again')
}

const emit = defineEmits<{
  (e: 'study-again'): void
}>()
</script>
