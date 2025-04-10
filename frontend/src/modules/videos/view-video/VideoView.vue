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
            
            <!-- Snippet List -->
            <div v-if="snippets.length > 0" class="mt-4">
              <h3 class="text-lg font-semibold mb-2">Snippets</h3>
              <div class="space-y-2">
                <div 
                  v-for="(snippet, index) in snippets" 
                  :key="index"
                  class="p-2 border rounded hover:bg-base-200 cursor-pointer"
                >
                  <div class="flex justify-between">
                    <span>Snippet {{ index + 1 }}</span>
                    <span class="text-sm text-gray-500">
                      {{ formatTime(snippet.startTime) }} - {{ formatTime(snippet.endTime) }}
                    </span>
                  </div>
                </div>
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
import { ref, onMounted } from 'vue';
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
