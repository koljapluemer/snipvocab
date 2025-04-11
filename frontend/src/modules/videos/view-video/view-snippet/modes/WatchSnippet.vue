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

      <!-- Controls Container -->
      <div class="flex flex-col items-center space-y-4">
        <!-- Rating Widget -->
        <transition name="fade">
          <div v-if="state === 'rating'" class="w-full max-w-md space-y-2">
            <label class="label">
              <span class="label-text">How well did you understand the snippet?</span>
            </label>
            <div class="flex items-center gap-4 mt-4">
              <span class="text-sm text-gray-500">Not at all</span>
              <input 
                type="range" 
                min="0" 
                max="100" 
                v-model="difficultyRating" 
                class="range flex-1" 
                :class="{
                  'range-primary': hasInteracted,
                  'range-base-300': !hasInteracted
                }"
                :disabled="isSubmitting"
                @input="onRatingChange"
              />
              <span class="text-sm text-gray-500">100%, easy</span>
            </div>
            <div class="flex gap-2 mt-4">
              <button @click="replaySnippet" class="btn btn-primary btn-sm">
                Replay Snippet
              </button>
              <button 
                @click="submitDifficulty" 
                class="btn btn-primary btn-sm"
                :disabled="isSubmitting || !hasInteracted"
                :class="{ 'loading': isSubmitting }"
              >
                {{ isSubmitting ? 'Saving...' : 'Save Rating' }}
              </button>
            </div>
          </div>
        </transition>

        <!-- Next Snippet Button -->
        <transition name="fade">
          <button 
            v-if="state === 'completed'" 
            @click="onNextSnippet" 
            class="btn btn-success"
          >
            Next Snippet
          </button>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import type { Snippet } from '@/shared/types/domainTypes'
import { updateSnippetPractice } from '@/modules/backend-communication/api'

const props = defineProps<{
  snippet: Snippet
}>()

const replayKey = ref(Date.now())
const difficultyRating = ref(50) // Default to middle value
const isSubmitting = ref(false)
const state = ref<'initial' | 'rating' | 'completed'>('initial')
const hasInteracted = ref(false)

// Configuration
const RATING_DELAY_MS = 2000 // 2 seconds delay before showing rating

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

const onRatingChange = () => {
  hasInteracted.value = true
}

const submitDifficulty = async () => {
  if (isSubmitting.value || !hasInteracted.value) return
  
  try {
    isSubmitting.value = true
    await updateSnippetPractice(
      props.snippet.videoId,
      props.snippet.index,
      difficultyRating.value
    )
    state.value = 'completed'
  } catch (error) {
    console.error('Failed to submit difficulty rating:', error)
    // You might want to show an error message to the user here
  } finally {
    isSubmitting.value = false
  }
}

const emit = defineEmits<{
  (e: 'study-again'): void
  (e: 'next-snippet'): void
}>()

const onStudyAgain = () => {
  emit('study-again')
}

const onNextSnippet = () => {
  emit('next-snippet')
}

// Start the state machine
onMounted(() => {
  // Show rating widget after delay
  setTimeout(() => {
    state.value = 'rating'
  }, RATING_DELAY_MS)
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
