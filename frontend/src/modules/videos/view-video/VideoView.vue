<template>
  <div class="container mx-auto p-4">
    <div class="max-w-2xl mx-auto">
      <!-- Show video details when not practicing -->
      <div v-if="currentSnippetIndex === null" class="card bg-base-100 shadow-xl">
        <figure>
          <img :src="`https://img.youtube.com/vi/${videoId}/hqdefault.jpg`" :alt="`Thumbnail for video ${videoId}`"
            class="w-full h-96 object-cover" />
        </figure>
        <div class="card-body">
          <div v-if="isLoading" class="flex justify-center">
            <span class="loading loading-spinner loading-lg"></span>
          </div>
          <div v-else-if="error" class="alert alert-error">
            {{ error }}
          </div>
          <div v-else>
            <div class="flex justify-between items-center">
              <button 
                v-if="enrichedSnippets.length > 0"
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
import type { EnrichedSnippetDetails } from '@/shared/types/domainTypes';
import { getVideoSnippets, getVideoEnrichedSnippets } from '@/modules/backend-communication/api';
import SnippetView from './view-snippet/SnippetView.vue';
import SnippetTimeline from './components/SnippetTimeline.vue';

const route = useRoute();
const videoId = route.params.videoId as string;
const enrichedSnippets = ref<EnrichedSnippetDetails[]>([]);
const currentSnippetIndex = ref<number | null>(null);
const isLoading = ref(true);
const error = ref<string | null>(null);

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

const startPractice = () => {
  if (enrichedSnippets.value.length > 0) {
    currentSnippetIndex.value = firstUnratedSnippetIndex.value;
  }
};

const handleNextSnippet = () => {
  if (currentSnippetIndex.value !== null && currentSnippetIndex.value < enrichedSnippets.value.length - 1) {
    currentSnippetIndex.value++;
  }
};

const refreshEnrichedSnippets = async () => {
  try {
    enrichedSnippets.value = await getVideoEnrichedSnippets(videoId);
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
