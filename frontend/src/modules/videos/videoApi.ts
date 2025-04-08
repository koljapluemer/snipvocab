import { api, handleApiResponse } from '@/modules/backend-communication/api'

export interface Snippet {
  id: number
  index: number
  start: number
  duration: number
  start_time: number
  end_time: number
}

export const getVideoSnippets = async (youtubeId: string): Promise<Snippet[]> => {
  return handleApiResponse<Snippet[]>(api.get(`/learn/videos/${youtubeId}/snippets/`))
}

export const getNumberOfSnippetsOfVideo = async (youtubeId: string): Promise<number> => {
  const snippets = await getVideoSnippets(youtubeId)
  return snippets.length
} 