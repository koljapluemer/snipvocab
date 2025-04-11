<template>
  <div class="container mx-auto p-4">
    <div class="max-w-2xl mx-auto">
      <!-- Show video details when not practicing -->
      <div v-if="currentSnippetIndex === null" class="card bg-base-100 shadow-xl">
        <figure>
          <img
            :src="`https://img.youtube.com/vi/${videoId}/hqdefault.jpg`"
            :alt="`Thumbnail for video ${videoId}`"
            class="w-full h-96 object-cover"
          />
        </figure>
        <div class="card-body">
          <h2 class="card-title">Video Details</h2>
          <div v-if="isLoading" class="flex justify-center">
            <span class="loading loading-spinner loading-lg"></span>
          </div>
          <div v-else-if="error" class="alert alert-error">
            {{ error }}
          </div>
          <div v-else>
            <div class="flex justify-between items-center">
              <div class="text-lg">
                {{ snippets.length }} snippets available
              </div>
              <button 
                v-if="snippets.length > 0"
                @click="startPractice" 
                class="btn btn-primary"
              >
                Start Practice
              </button>
            </div>
            
            <!-- Snippet Timeline -->
            <div v-if="snippets.length > 0" class="mt-8">
              <h3 class="text-lg font-semibold mb-4">Snippets Timeline</h3>
              <div class="relative w-full h-12 bg-base-200 rounded-lg overflow-hidden">
                <div 
                  v-for="(snippet, index) in snippets" 
                  :key="index"
                  class="absolute h-full cursor-pointer transition-all duration-200 hover:bg-primary/20"
                  :class="[
                    index % 2 === 0 ? 'bg-base-300' : 'bg-base-200',
                    currentSnippetIndex === index ? 'ring-2 ring-primary' : ''
                  ]"
                  :style="{
                    left: `${(snippet.startTime / totalDuration) * 100}%`,
                    width: `${((snippet.endTime - snippet.startTime) / totalDuration) * 100}%`
                  }"
                  :title="`Snippet ${index + 1}: ${formatTime(snippet.startTime)} - ${formatTime(snippet.endTime)}`"
                  @click="jumpToSnippet(index)"
                />
              </div>
              <div class="flex justify-between mt-2 text-sm text-gray-500">
                <span>0:00</span>
                <span>{{ formatTime(totalDuration) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Show SnippetView when practicing -->
      <SnippetView
        v-if="currentSnippetIndex !== null && snippets.length > 0"
        :snippet="snippets[currentSnippetIndex]"
        @next-snippet="handleNextSnippet"
        @back-to-video="currentSnippetIndex = null"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import type { Snippet } from '@/shared/types/domainTypes';
import { getVideoSnippets } from '@/modules/backend-communication/api';
import SnippetView from './view-snippet/SnippetView.vue';

const route = useRoute();
const videoId = route.params.videoId as string;
const snippets = ref<Snippet[]>([]);
const currentSnippetIndex = ref<number | null>(null);
const isLoading = ref(true);
const error = ref<string | null>(null);

// Compute total duration from the last snippet's end time
const totalDuration = computed(() => {
  if (snippets.value.length === 0) return 0;
  return snippets.value[snippets.value.length - 1].endTime;
});

const formatTime = (seconds: number): string => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
};

const startPractice = () => {
  if (snippets.value.length > 0) {
    currentSnippetIndex.value = 0;
  }
};

const handleNextSnippet = () => {
  if (currentSnippetIndex.value !== null && currentSnippetIndex.value < snippets.value.length - 1) {
    currentSnippetIndex.value++;
  }
};

const jumpToSnippet = (index: number) => {
  currentSnippetIndex.value = index;
};

onMounted(async () => {
  try {
    snippets.value = await getVideoSnippets(videoId);
    isLoading.value = false;
  } catch (err: unknown) {
    console.error('Error fetching video data:', err);
    error.value = err instanceof Error ? err.message : 'Failed to load video snippets';
    isLoading.value = false;
  }
});
</script>
