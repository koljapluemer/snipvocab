<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import VideoTile from '@/modules/videos/video-list/VideoTile.vue'
import { getOnboardingVideos } from '@/modules/backend-communication/api'
import type { VideoInfo } from '@/modules/backend-communication/apiTypes'

const router = useRouter()
const videos = ref<VideoInfo[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
    try {
        videos.value = await getOnboardingVideos()
        console.log('Onboarding videos:', videos.value) // Debug log
    } catch (err) {
        error.value = err instanceof Error ? err.message : 'Failed to load videos'
    } finally {
        loading.value = false
    }
})
</script>

<template>
    <div class="max-w-3xl mx-auto text-center mb-12">
        <h1 class="text-4xl font-bold text-primary mb-4">Choose Your First Video</h1>
        <p class="text-lg text-base-content/80">
            Start your learning journey by picking one of these carefully selected videos.
            They're perfect for beginners and will help you get familiar with the learning process.
        </p>
    </div>

    <div v-if="loading" class="flex justify-center">
        <span class="loading loading-spinner loading-lg"></span>
    </div>

    <div v-else-if="error" class="alert alert-error max-w-3xl mx-auto">
        <span>{{ error }}</span>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
        <VideoTile v-for="video in videos" :key="video.youtube_id" :video-id="video.youtube_id"
            :title="video.youtube_title" />
    </div>

    <div class="flex flex-center mt-10">
        <router-link :to="{ name: 'home' }" class="link mx-auto text-sm text-center">
            Choose Another Video
        </router-link>
    </div>
</template>
