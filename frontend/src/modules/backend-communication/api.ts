import type { Snippet, Word, SnippetDetails, WordFlashCard, LearningEvent, EnrichedSnippetDetails } from '@/shared/types/domainTypes'
import axios from 'axios'
import type { AxiosResponse } from 'axios'

// API Response Types
export interface AuthUserResponse {
  email: string
}

export interface LoginResponse {
  access: string
  refresh: string
}

export interface RegisterResponse {
  tokens: {
    access: string
    refresh: string
  }
}

export interface SnippetPracticeResponse {
  perceived_difficulty: number | null;
  updated: string;
}

// Create axios instance with base configuration
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add auth token to requests if it exists
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
    return Promise.reject(error)
  }
)

// Helper function to handle API responses
export const handleApiResponse = async <T>(promise: Promise<AxiosResponse<T>>): Promise<T> => {
  try {
    const response = await promise
    return response.data
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || error.message)
    }
    throw error
  }
}

// Video API functions
export const getVideos = async (): Promise<string[]> => {
  try {
    return await handleApiResponse(api.get('/learn/videos/'))
  } catch (error) {
    console.error('Error fetching videos:', error)
    throw new Error('Failed to fetch videos. Please try again later.')
  }
}

export const getVideoSnippets = async (youtubeId: string): Promise<Snippet[]> => {
  try {
    return await handleApiResponse(api.get(`/learn/videos/${youtubeId}/snippets/`))
  } catch (error) {
    console.error('Error fetching video snippets:', error)
    throw new Error('Failed to fetch video snippets. Please try again later.')
  }
}

export const getSnippetDetails = async (youtubeId: string, index: number): Promise<SnippetDetails> => {
  try {
    return await handleApiResponse(api.get(`/learn/videos/${youtubeId}/snippets/${index}/`))
  } catch (error) {
    console.error('Error fetching snippet details:', error)
    throw new Error('Failed to fetch snippet details. Please try again later.')
  }
}

export const getSnippetDueWords = async (youtubeId: string, index: number): Promise<WordFlashCard[]> => {
  try {
    return await handleApiResponse(api.get(`/learn/videos/${youtubeId}/snippets/${index}/due-words/`))
  } catch (error) {
    console.error('Error fetching due words:', error)
    throw new Error('Failed to fetch due words. Please try again later.')
  }
}

export interface LearningEventResponse {
  originalWord: string
  success: boolean
  newDueDate?: string
  error?: string
}

export const sendLearningEvents = async (events: LearningEvent[]): Promise<LearningEventResponse[]> => {
  try {
    return await handleApiResponse(api.post('/learn/learning-events/', events))
  } catch (error) {
    console.error('Error sending learning events:', error)
    throw new Error('Failed to save learning progress. Please try again later.')
  }
}

export const getSnippetPractice = async (youtubeId: string, index: number): Promise<SnippetPracticeResponse> => {
  try {
    return await handleApiResponse(api.get(`/learn/videos/${youtubeId}/snippets/${index}/practice/`))
  } catch (error) {
    console.error('Error fetching snippet practice:', error)
    throw new Error('Failed to fetch snippet practice data. Please try again later.')
  }
}

export const updateSnippetPractice = async (
  youtubeId: string, 
  index: number, 
  perceivedDifficulty: number
): Promise<SnippetPracticeResponse> => {
  try {
    return await handleApiResponse(api.post(
      `/learn/videos/${youtubeId}/snippets/${index}/practice/`,
      { perceived_difficulty: perceivedDifficulty }
    ))
  } catch (error) {
    console.error('Error updating snippet practice:', error)
    throw new Error('Failed to update snippet practice data. Please try again later.')
  }
}

export const getVideoEnrichedSnippets = async (youtubeId: string): Promise<EnrichedSnippetDetails[]> => {
  try {
    return await handleApiResponse(api.get(`/learn/videos/${youtubeId}/enriched-snippets/`))
  } catch (error) {
    console.error('Error fetching enriched snippets:', error)
    throw new Error('Failed to fetch enriched snippets. Please try again later.')
  }
}
