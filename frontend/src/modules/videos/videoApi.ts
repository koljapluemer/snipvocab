import { api, handleApiResponse } from '@/modules/backend-communication/api'
import type { Snippet, Word } from '@/shared/types/domainTypes'

export const getVideoSnippets = async (youtubeId: string): Promise<Snippet[]> => {
  return handleApiResponse<Snippet[]>(api.get(`/learn/videos/${youtubeId}/snippets/`))
}

export const getNumberOfSnippetsOfVideo = async (youtubeId: string): Promise<number> => {
  const snippets = await getVideoSnippets(youtubeId)
  return snippets.length
}

export const getSnippetWords = async (youtubeId: string, snippetIndex: number): Promise<Word[]> => {
  return handleApiResponse<Word[]>(api.get(`/learn/videos/${youtubeId}/snippets/${snippetIndex}/words/`))
} 