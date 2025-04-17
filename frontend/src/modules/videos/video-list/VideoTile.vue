<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getVideoProgress } from '@/modules/backend-communication/api'

const props = defineProps<{
  videoId: string
  title: string | null
}>()

const router = useRouter()
const lastPracticed = ref<string | null>(null)
const progressPercentage = ref<number>(0)
const loading = ref(true)

const handleViewVideo = () => {
  router.push({ name: 'video', params: { videoId: props.videoId }})
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

onMounted(async () => {
  try {
    const progress = await getVideoProgress(props.videoId)
    
    if (progress.lastPracticed) {
      const formattedDate = formatDate(progress.lastPracticed)
      lastPracticed.value = formattedDate
    } else {
    }
    if (progress.snippetPercentageWatched !== null) {
      progressPercentage.value = progress.snippetPercentageWatched
    }
  } catch (error) {
    console.error('Error fetching video progress:', error)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="group cursor-pointer" @click="handleViewVideo">
    <div class="relative overflow-hidden rounded-lg aspect-video">
      <img 
        :src="`https://img.youtube.com/vi/${videoId}/mqdefault.jpg`" 
        :alt="`Video thumbnail for ${videoId}`"
        class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
      />
      <div class="absolute inset-0 bg-black/20 group-hover:bg-black/30 transition-colors duration-300" />
      <div 
        v-if="!loading && lastPracticed" 
        class="absolute top-2 right-2 bg-black/70 text-white px-2 py-1 rounded"
      >
        Last practiced {{ lastPracticed }}
      </div>
      <progress 
        v-if="progressPercentage > 0"
        class="progress progress-primary w-full absolute bottom-0 left-0" 
        :value="progressPercentage" 
        max="100"
      ></progress>
    </div>
    <div class="mt-2">
      <h3 class="line-clamp-2 text-lg" :title="title || ''">
        {{ title || 'Untitled Video' }}
      </h3>
    </div>
  </div>
</template>
