<template>
  <div class="container mx-auto p-4">
    <div class="max-w-2xl mx-auto">
      <div class="card bg-base-100 shadow-xl">
        <figure>
          <img
            :src="`https://img.youtube.com/vi/${videoId}/hqdefault.jpg`"
            :alt="`Thumbnail for video ${videoId}`"
            class="w-full h-96 object-cover"
          />
        </figure>
        <div class="card-body">
          <h2 class="card-title">Video Details</h2>
          <div class="flex justify-between items-center">
            <div class="text-lg">
              {{ snippetCount }} snippets available
            </div>
            <router-link 
              v-if="snippetCount > 0"
              :to="{ name: 'snippet', params: { videoId, index: 0 }}" 
              class="btn btn-primary"
            >
              Start Practice
            </router-link>
          </div>
          
          <!-- Snippet List -->
          <div v-if="snippets.length > 0" class="mt-4">
            <h3 class="text-lg font-semibold mb-2">Snippets</h3>
            <div class="space-y-2">
              <div 
                v-for="snippet in snippets" 
                :key="snippet.id"
                class="p-2 border rounded hover:bg-base-200 cursor-pointer"
                @click="router.push({ name: 'snippet', params: { videoId, index: snippet.index }})"
              >
                <div class="flex justify-between">
                  <span>Snippet {{ snippet.index + 1 }}</span>
                  <span class="text-sm text-gray-500">
                    {{ formatTime(snippet.start_time) }} - {{ formatTime(snippet.end_time) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getNumberOfSnippetsOfVideo, getVideoSnippets, type Snippet } from '@/modules/videos/videoApi';

const route = useRoute();
const router = useRouter();
const videoId = route.params.videoId as string;
const snippetCount = ref<number>(0);
const snippets = ref<Snippet[]>([]);

const formatTime = (seconds: number): string => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
};

onMounted(async () => {
  try {
    snippets.value = await getVideoSnippets(videoId);
    snippetCount.value = snippets.value.length;
  } catch (error) {
    console.error('Error fetching video data:', error);
  }
});
</script>
