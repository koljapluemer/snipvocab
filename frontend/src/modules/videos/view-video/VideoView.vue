<template>
  <div class="container mx-auto p-4">
    <div class="max-w-2xl mx-auto">
      <!-- Show video details when not practicing -->
      <div v-if="currentSnippetIndex === null" class="card bg-base-100 shadow-xl">
        <figure>
          <div v-if="isComplete" class="w-full aspect-video">
            <iframe 
              :src="`https://www.youtube.com/embed/${videoId}`"
              class="w-full h-full"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowfullscreen
            ></iframe>
          </div>
          <img v-else :src="`https://img.youtube.com/vi/${videoId}/hqdefault.jpg`" 
            :alt="`Thumbnail for video ${videoId}`"
            class="w-full h-96 object-cover" 
          />
        </figure>
        <div class="card-body">
          <div v-if="isLoading" class="flex justify-center">
            <span class="loading loading-spinner loading-lg"></span>
          </div>
          <div v-else-if="error" class="alert alert-error">
            {{ error }}
          </div>
          <div v-else>
            <h2 class="card-title text-2xl mb-4">{{ videoTitle }}</h2>
            <div class="mb-4">
              <div v-if="isComplete" class="text-center py-4">
                <div class="text-4xl mb-2">🏆</div>
                <h3 class="text-xl font-bold text-primary">You are done!</h3>
                <p class="text-gray-600">Congratulations on completing this video!</p>
              </div>
              <div v-else>
                <div class="flex justify-between mb-1">
                  <span class="text-sm font-medium">Progress</span>
                  <span class="text-sm font-medium">{{ Math.round(progressPercentage) }}%</span>
                </div>
                <progress class="progress progress-primary w-full" :value="progressPercentage" max="100"></progress>
              </div>
            </div>
            <div class="flex justify-between items-center">
              <button 
                v-if="enrichedSnippets.length > 0 && !isComplete"
                @click="startPractice" 
                class="btn btn-primary"
              >
                {{ hasUnratedSnippets ? 'Practice Next Snippet' : 'Start Practice' }}
              </button>
            </div>

            <!-- Snippet Timeline -->
            <SnippetTimeline
              v-if="enrichedSnippets.length > 0"
              :enriched-snippets="enrichedSnippets"
              :current-snippet-index="currentSnippetIndex"
              @jump-to-snippet="jumpToSnippet"
            />
          </div>
        </div>
      </div>

      <!-- Show SnippetView when practicing -->
      <SnippetView v-if="currentSnippetIndex !== null && enrichedSnippets.length > 0" 
        :snippet="enrichedSnippets[currentSnippetIndex]"
        @next-snippet="handleNextSnippet" 
        @back-to-video="async () => {
          currentSnippetIndex = null;
          await refreshEnrichedSnippets();
        }" 
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import type { EnrichedSnippetDetails } from '@/shared/domainTypes';
import { getVideoSnippets, getVideoEnrichedSnippets, updateVideoProgress } from '@/modules/backend-communication/api';
import SnippetView from './view-snippet/SnippetView.vue';
import SnippetTimeline from './components/SnippetTimeline.vue';

const route = useRoute();
const videoId = route.params.videoId as string;
const enrichedSnippets = ref<EnrichedSnippetDetails[]>([]);
const currentSnippetIndex = ref<number | null>(null);
const isLoading = ref(true);
const error = ref<string | null>(null);
const videoTitle = ref<string>('');

// Calculate progress based on rated snippets
const progressPercentage = computed(() => {
  if (enrichedSnippets.value.length === 0) return 0;
  const ratedSnippets = enrichedSnippets.value.filter(snippet => 
    snippet.perceivedDifficulty !== null
  ).length;
  return (ratedSnippets / enrichedSnippets.value.length) * 100;
});

// Find the first unrated snippet index
const firstUnratedSnippetIndex = computed(() => {
  if (enrichedSnippets.value.length === 0) {
    return 0;
  }
  return enrichedSnippets.value.findIndex(snippet => snippet.perceivedDifficulty === null) ?? 0;
});

// Check if all snippets are rated
const hasUnratedSnippets = computed(() => {
  if (enrichedSnippets.value.length === 0) {
    return true;
  }
  return enrichedSnippets.value.some(snippet => snippet.perceivedDifficulty === null);
});

// Add isComplete computed property
const isComplete = computed(() => {
  return progressPercentage.value >= 100;
});

const startPractice = () => {
  if (enrichedSnippets.value.length > 0) {
    currentSnippetIndex.value = firstUnratedSnippetIndex.value;
  }
};

const handleNextSnippet = async () => {
  if (currentSnippetIndex.value !== null && currentSnippetIndex.value < enrichedSnippets.value.length - 1) {
    currentSnippetIndex.value++;
    // Update video progress after moving to next snippet
    try {
      await updateVideoProgress(videoId, {
        snippetPercentageWatched: progressPercentage.value
      });
    } catch (err) {
      console.error('Error updating video progress:', err);
    }
  }
};

const refreshEnrichedSnippets = async () => {
  try {
    const response = await getVideoEnrichedSnippets(videoId);
    enrichedSnippets.value = response.snippets;
    videoTitle.value = response.title;
    // If we have progress data, update the video progress
    if (response.snippetPercentageWatched !== null) {
      await updateVideoProgress(videoId, {
        snippetPercentageWatched: response.snippetPercentageWatched,
        perceivedDifficulty: response.perceivedDifficulty ?? undefined
      });
    }
  } catch (err: unknown) {
    console.error('Error refreshing enriched snippets:', err);
  }
};

const jumpToSnippet = (index: number) => {
  currentSnippetIndex.value = index;
};

onMounted(async () => {
  try {
    await refreshEnrichedSnippets();
    isLoading.value = false;
  } catch (err: unknown) {
    console.error('Error fetching video data:', err);
    error.value = err instanceof Error ? err.message : 'Failed to load video snippets';
    isLoading.value = false;
  }
});
</script>
