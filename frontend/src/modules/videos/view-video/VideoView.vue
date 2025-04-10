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
                v-if="snippets.length > 0"
                @click="startPractice" 
                class="btn btn-primary"
              >
                {{ hasUnratedSnippets ? 'Practice Next Snippet' : 'Start Practice' }}
              </button>
            </div>

            <!-- Snippet Timeline -->
            <div v-if="snippets.length > 0 && enrichedSnippets.length === snippets.length" class="mt-8">
              <h3 class="text-lg font-semibold mb-4">Snippets Timeline</h3>
              <div class="relative w-full h-12 bg-base-200 rounded-lg overflow-hidden">
                <div v-for="(snippet, index) in snippets" :key="index"
                  class="absolute h-full cursor-pointer transition-all duration-200" :class="[
                    currentSnippetIndex === index ? 'ring-2 ring-primary' : '',
                    'hover:brightness-110 hover:scale-[1.02]'
                  ]" :style="{
                    left: `${(snippet.startTime / totalDuration) * 100}%`,
                    width: `${((snippet.endTime - snippet.startTime) / totalDuration) * 100}%`,
                    backgroundColor: getDifficultyColor(enrichedSnippets[index]?.perceivedDifficulty ?? null, index)
                  }" :title="`Snippet ${index + 1}: ${formatTime(snippet.startTime)} - ${formatTime(snippet.endTime)}
Difficulty: ${enrichedSnippets[index]?.perceivedDifficulty ?? 'Not rated'}`" @click="jumpToSnippet(index)" />
              </div>
              <div class="flex justify-between mt-2 text-sm text-gray-500">
                <span>0:00</span>
                <span>{{ formatTime(totalDuration) }}</span>
              </div>
              <div class="flex justify-between mt-2 text-xs text-gray-500">
                <span>Hard (0)</span>
                <span>Easy (100)</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Show SnippetView when practicing -->
      <SnippetView v-if="currentSnippetIndex !== null && snippets.length > 0" :snippet="snippets[currentSnippetIndex]"
        @next-snippet="handleNextSnippet" @back-to-video="async () => {
          currentSnippetIndex = null;
          await refreshEnrichedSnippets();
        }" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import type { Snippet, EnrichedSnippetDetails } from '@/shared/types/domainTypes';
import { getVideoSnippets, getVideoEnrichedSnippets } from '@/modules/backend-communication/api';
import SnippetView from './view-snippet/SnippetView.vue';

const route = useRoute();
const videoId = route.params.videoId as string;
const snippets = ref<Snippet[]>([]);
const enrichedSnippets = ref<EnrichedSnippetDetails[]>([]);
const currentSnippetIndex = ref<number | null>(null);
const isLoading = ref(true);
const error = ref<string | null>(null);

// Find the first unrated snippet index
const firstUnratedSnippetIndex = computed(() => {
  if (snippets.value.length === 0 || enrichedSnippets.value.length !== snippets.value.length) {
    return 0; // If no data yet, default to first snippet
  }
  return enrichedSnippets.value.findIndex(snippet => snippet.perceivedDifficulty === null) ?? 0;
});

// Check if all snippets are rated
const hasUnratedSnippets = computed(() => {
  if (snippets.value.length === 0 || enrichedSnippets.value.length !== snippets.value.length) {
    return true; // If no data yet, assume there are unrated snippets
  }
  return enrichedSnippets.value.some(snippet => snippet.perceivedDifficulty === null);
});

// Compute total duration from the last snippet's end time
const totalDuration = computed(() => {
  if (snippets.value.length === 0) return 0;
  return snippets.value[snippets.value.length - 1].endTime;
});

// Compute color based on difficulty (0-100)
const getDifficultyColor = (difficulty: number | null, index: number) => {
  if (difficulty === null) {
    // Alternate between light and dark gray for unrated snippets
    return index % 2 === 0 ? 'bg-base-100' : 'bg-base-300';
  }

  // Map difficulty to HSL color space
  // 0 -> 120 (green), 50 -> yellow, 100 -> 0 (red)
  const hue = difficulty * 1.2; // 0 is green, 120 is red
  const saturation = 100;
  const lightness = 45; // Keep it dark enough for good contrast

  return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
};

const formatTime = (seconds: number): string => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
};

const startPractice = () => {
  if (snippets.value.length > 0) {
    currentSnippetIndex.value = firstUnratedSnippetIndex.value;
  }
};

const handleNextSnippet = () => {
  if (currentSnippetIndex.value !== null && currentSnippetIndex.value < snippets.value.length - 1) {
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
    snippets.value = await getVideoSnippets(videoId);
    await refreshEnrichedSnippets();
    isLoading.value = false;
  } catch (err: unknown) {
    console.error('Error fetching video data:', err);
    error.value = err instanceof Error ? err.message : 'Failed to load video snippets';
    isLoading.value = false;
  }
});
</script>
