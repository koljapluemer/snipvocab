import { ref, readonly } from 'vue'
import type { Snippet, Word, SnippetDetails, WordFlashCard, LearningEvent, EnrichedSnippetDetails } from '@/shared/domainTypes'
import type { 
  AuthUserResponse, 
  LoginResponse, 
  RegisterResponse, 
  SnippetPracticeResponse, 
  VideoProgressResponse, 
  EnrichedSnippetsResponse, 
  VideoInfo, 
  PaginatedResponse, 
  UserInfoResponse, 
  SubscriptionInfoResponse 
} from './apiTypes'
import axios from 'axios'
import type { AxiosResponse } from 'axios'

// Auth state management
const authState = {
  userEmail: ref(''),
  isAuthenticated: ref(false),
  isLoading: ref(true),
  error: ref<string | null>(null),
  isInitialized: ref(false)
}

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

// Create axios instance with base configuration
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': import.meta.env.VITE_FRONTEND_API_KEY
  },
  withCredentials: true
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
      clearAuthState()
    }
    return Promise.reject(error)
  }
)

// Helper function to clear auth state
const clearAuthState = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user_id')
  authState.isAuthenticated.value = false
  authState.userEmail.value = ''
  authState.error.value = null
}

// Auth state functions
export const checkAuth = async () => {
  try {
    authState.isLoading.value = true
    authState.error.value = null
    
    const response = await handleApiResponse<AuthUserResponse>(api.get('/auth/user/'))
    authState.isAuthenticated.value = true
    authState.userEmail.value = response.email
  } catch (error) {
    clearAuthState()
  } finally {
    authState.isLoading.value = false
    authState.isInitialized.value = true
  }
}

export const login = async (email: string, password: string) => {
  try {
    authState.isLoading.value = true
    authState.error.value = null
    
    const response = await handleApiResponse<LoginResponse>(api.post('/auth/login/', {
      username: email,
      password
    }))
    
    localStorage.setItem('access_token', response.access)
    localStorage.setItem('refresh_token', response.refresh)
    authState.isAuthenticated.value = true
    authState.userEmail.value = email
  } catch (error) {
    authState.error.value = error instanceof Error ? error.message : 'Login failed'
    throw error
  } finally {
    authState.isLoading.value = false
  }
}

export const logout = () => {
  clearAuthState()
}

export const register = async (email: string, password: string) => {
  try {
    authState.isLoading.value = true
    authState.error.value = null
    
    const response = await handleApiResponse<RegisterResponse>(api.post('/auth/register/', {
      email,
      password
    }))
    
    localStorage.setItem('access_token', response.tokens.access)
    localStorage.setItem('refresh_token', response.tokens.refresh)
    authState.isAuthenticated.value = true
    authState.userEmail.value = email
  } catch (error) {
    authState.error.value = error instanceof Error ? error.message : 'Registration failed'
    throw error
  } finally {
    authState.isLoading.value = false
  }
}

// Initialize auth state
const initializeAuth = async () => {
  const token = localStorage.getItem('access_token')
  
  if (!token) {
    clearAuthState()
    authState.isInitialized.value = true
    authState.isLoading.value = false
    return
  }

  try {
    await checkAuth()
  } catch (error) {
    // If checkAuth fails, we've already cleared the state
  }
}

// Start initialization
initializeAuth()

// Export auth state composable
export const useAuthState = () => {
  return {
    // Readonly state to prevent direct mutations
    userEmail: readonly(authState.userEmail),
    isAuthenticated: readonly(authState.isAuthenticated),
    isLoading: readonly(authState.isLoading),
    isInitialized: readonly(authState.isInitialized),
    error: readonly(authState.error),
    // Actions
    login,
    logout,
    register,
    checkAuth
  }
}

// Video API functions
export const getVideos = async (page: number = 1, pageSize: number = 10): Promise<PaginatedResponse<VideoInfo>> => {
  try {
    return await handleApiResponse(api.get(`/learn/videos/?page=${page}&page_size=${pageSize}`))
  } catch (error) {
    console.error('Error fetching videos:', error)
    throw new Error('Failed to fetch videos. Please try again later.')
  }
}

export const getVideosByTag = async (tagName: string, page: number = 1, pageSize: number = 10): Promise<PaginatedResponse<VideoInfo>> => {
  try {
    return await handleApiResponse(api.get(`/learn/videos/tag/${tagName}/?page=${page}&page_size=${pageSize}`))
  } catch (error) {
    console.error('Error fetching videos by tag:', error)
    throw new Error('Failed to fetch videos by tag. Please try again later.')
  }
}

export const getNewestVideos = async (page: number = 1, pageSize: number = 10): Promise<PaginatedResponse<VideoInfo>> => {
  try {
    return await handleApiResponse(api.get(`/learn/videos/new/?page=${page}&page_size=${pageSize}`))
  } catch (error) {
    console.error('Error fetching newest videos:', error)
    throw new Error('Failed to fetch newest videos. Please try again later.')
  }
}

export const getPopularVideos = async (page: number = 1, pageSize: number = 10): Promise<PaginatedResponse<VideoInfo>> => {
  try {
    return await handleApiResponse(api.get(`/learn/videos/popular/?page=${page}&page_size=${pageSize}`))
  } catch (error) {
    console.error('Error fetching popular videos:', error)
    throw new Error('Failed to fetch popular videos. Please try again later.')
  }
}

export const getRandomCommonTag = async (): Promise<string> => {
  try {
    return await handleApiResponse(api.get('/learn/tags/random/'))
  } catch (error) {
    console.error('Error fetching random tag:', error)
    throw new Error('Failed to fetch random tag. Please try again later.')
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

export const getSnippetAllWords = async (youtubeId: string, index: number): Promise<WordFlashCard[]> => {
  try {
    return await handleApiResponse(api.get(`/learn/videos/${youtubeId}/snippets/${index}/all-words/`))
  } catch (error) {
    console.error('Error fetching all words:', error)
    throw new Error('Failed to fetch words. Please try again later.')
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

export const getVideoEnrichedSnippets = async (youtubeId: string): Promise<EnrichedSnippetsResponse> => {
  try {
    return await handleApiResponse(api.get(`/learn/videos/${youtubeId}/enriched-snippets/`))
  } catch (error) {
    console.error('Error fetching enriched snippets:', error)
    throw new Error('Failed to fetch enriched snippets. Please try again later.')
  }
}

export const getVideoProgress = async (videoId: string): Promise<VideoProgressResponse> => {
  try {
    return await handleApiResponse(api.get(`/learn/videos/${videoId}/progress/`))
  } catch (error) {
    console.error('Error fetching video progress:', error)
    throw new Error('Failed to fetch video progress. Please try again later.')
  }
}

export const updateVideoProgress = async (
  youtubeId: string,
  data: {
    perceivedDifficulty?: number;
    snippetPercentageWatched?: number;
  }
): Promise<VideoProgressResponse> => {
  try {
    return await handleApiResponse(api.post(`/learn/videos/${youtubeId}/progress/`, data))
  } catch (error) {
    console.error('Error updating video progress:', error)
    throw new Error('Failed to update video progress. Please try again later.')
  }
}

// Payment API functions
export const createCheckoutSession = async (): Promise<{ checkoutUrl: string }> => {
  try {
    return await handleApiResponse(api.post('/payment/create-checkout-session/'))
  } catch (error) {
    console.error('Error creating checkout session:', error)
    throw new Error('Failed to create checkout session. Please try again later.')
  }
}

export const createCustomerPortalSession = async (): Promise<{ portalUrl: string }> => {
  try {
    return await handleApiResponse(api.post('/payment/create-portal-session/'))
  } catch (error) {
    console.error('Error creating customer portal session:', error)
    throw new Error('Failed to access customer portal. Please try again later.')
  }
}

export const getUserInfo = async (): Promise<UserInfoResponse> => {
  try {
    return await handleApiResponse(api.get('/auth/user/'))
  } catch (error) {
    console.error('Error fetching user info:', error)
    throw new Error('Failed to fetch user information. Please try again later.')
  }
}

export const getSubscriptionInfo = async (): Promise<SubscriptionInfoResponse> => {
  try {
    return await handleApiResponse(api.get('/payment/subscription-info/'))
  } catch (error) {
    console.error('Error fetching subscription info:', error)
    throw new Error('Failed to fetch subscription information. Please try again later.')
  }
}

export const cancelSubscription = async (): Promise<{ message: string }> => {
  try {
    return await handleApiResponse(api.post('/payment/cancel-subscription/'))
  } catch (error) {
    console.error('Error canceling subscription:', error)
    throw new Error('Failed to cancel subscription. Please try again later.')
  }
}

// Password Reset API functions
export const requestPasswordReset = async (email: string): Promise<{ message: string }> => {
  try {
    return await handleApiResponse(api.post('/auth/password-reset/', { email }))
  } catch (error) {
    console.error('Error requesting password reset:', error)
    throw new Error('Failed to request password reset. Please try again later.')
  }
}

export const confirmPasswordReset = async (uid: string, token: string, password: string): Promise<{ message: string }> => {
  try {
    return await handleApiResponse(api.post('/auth/password-reset/confirm/', {
      uid,
      token,
      password
    }))
  } catch (error) {
    console.error('Error confirming password reset:', error)
    throw new Error('Failed to reset password. Please try again later.')
  }
}
