<template>
  <div class="card bg-base-100 shadow-xl">
    <figure>
      <img :src="`https://img.youtube.com/vi/${videoId}/hqdefault.jpg`" :alt="`Thumbnail for video ${videoId}`" class="w-full h-48 object-cover" />
    </figure>
    <div class="card-body">
      <div class="flex justify-between items-center">
        <div class="text-sm text-gray-500">
          {{ snippetCount }} snippets
        </div>
        <router-link 
          :to="{ name: 'video', params: { videoId }}"
          class="btn btn-primary"
        >
          View Details
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getNumberOfSnippetsOfVideo } from '@/modules/videos/videoApi';

const props = defineProps<{
  videoId: string;
}>();

const snippetCount = ref<number>(0);

onMounted(async () => {
  try {
    snippetCount.value = await getNumberOfSnippetsOfVideo(props.videoId);
  } catch (error) {
    console.error('Error fetching snippet count:', error);
  }
});
</script>
