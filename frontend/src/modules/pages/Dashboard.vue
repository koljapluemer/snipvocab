<script setup lang="ts">
import VideoList from '@/modules/videos/video-list/VideoList.vue'
import { DisplaySource } from '@/modules/videos/video-list/types'
</script>

<template>
    <VideoList :source="DisplaySource.NEWEST_VIDEOS" />
    <VideoList :source="DisplaySource.POPULAR_VIDEOS" />
    <VideoList :source="DisplaySource.VIDEOS_WITH_TAG" tag="افكار" />
    <VideoList :source="DisplaySource.ALL_VIDEOS" />
</template>
