import { ref } from 'vue'
import { api, handleApiResponse } from '../backend-communication/api'
import type { AuthUserResponse, LoginResponse, RegisterResponse } from '../backend-communication/api'

// Shared state
const userEmail = ref('')
const isAuthenticated = ref(false)

const checkAuth = async () => {
  try {
    const response = await handleApiResponse<AuthUserResponse>(api.get('/auth/user/'))
    isAuthenticated.value = true
    userEmail.value = response.email
  } catch (error) {
    isAuthenticated.value = false
    userEmail.value = ''
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }
}

const login = async (email: string, password: string) => {
  const response = await handleApiResponse<LoginResponse>(api.post('/auth/login/', {
    username: email,
    password
  }))
  
  localStorage.setItem('access_token', response.access)
  localStorage.setItem('refresh_token', response.refresh)
  isAuthenticated.value = true
  userEmail.value = email
}

const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  isAuthenticated.value = false
  userEmail.value = ''
}

const register = async (email: string, password: string) => {
  const response = await handleApiResponse<RegisterResponse>(api.post('/auth/register/', {
    email,
    password
  }))
  
  localStorage.setItem('access_token', response.tokens.access)
  localStorage.setItem('refresh_token', response.tokens.refresh)
  isAuthenticated.value = true
  userEmail.value = email
}

// Check initial auth status
const token = localStorage.getItem('access_token')
if (token) {
  checkAuth()
} else {
  isAuthenticated.value = false
  userEmail.value = ''
}

export const useAuthState = () => {
  return {
    userEmail,
    isAuthenticated,
    login,
    logout,
    register
  }
} 