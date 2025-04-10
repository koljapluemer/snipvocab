import { ref } from 'vue'
import { useApi } from './composables/useApi'
import type { Video, Snippet } from './types'

const { api } = useApi()

export const getVideos = async (): Promise<string[]> => {
  try {
    const response = await api.get('/videos/')
    return response.data
  } catch (error) {
    console.error('Error fetching videos:', error)
    throw error
  }
}

export const getVideoSnippets = async (youtubeId: string): Promise<Snippet[]> => {
  try {
    const response = await api.get(`/videos/${youtubeId}/snippets/`)
    return response.data
  } catch (error) {
    console.error(`Error fetching snippets for video ${youtubeId}:`, error)
    throw error
  }
} 