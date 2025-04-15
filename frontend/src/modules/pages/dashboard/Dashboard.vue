<script setup lang="ts">
import { ref, onMounted } from 'vue'
import VideoList from '@/modules/videos/video-list/VideoList.vue'
import { DisplaySource } from '@/modules/videos/video-list/types'
import { getRandomCommonTag } from '@/modules/backend-communication/api'

const randomTags = ref<string[]>(['', '', ''])
const loadingTags = ref(true)

const fetchRandomTags = async () => {
  loadingTags.value = true
  try {
    randomTags.value = await Promise.all([
      getRandomCommonTag(),
      getRandomCommonTag(),
      getRandomCommonTag()
    ])
  } catch (error) {
    console.error('Failed to fetch random tags:', error)
  } finally {
    loadingTags.value = false
  }
}

onMounted(() => {
  fetchRandomTags()
})
</script>

<template>
    <VideoList :source="DisplaySource.NEWEST_VIDEOS" />
    <VideoList :source="DisplaySource.POPULAR_VIDEOS" />
    <template v-if="!loadingTags">
      <VideoList v-for="(tag, index) in randomTags" :key="index" 
        :source="DisplaySource.VIDEOS_WITH_TAG" 
        :tag="tag" 
      />
    </template>
    <VideoList :source="DisplaySource.ALL_VIDEOS" />
</template>
