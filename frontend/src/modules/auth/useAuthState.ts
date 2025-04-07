import { ref } from 'vue'
import axios from 'axios'

const api = axios.create({
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

// Shared state
const userEmail = ref('')
const isAuthenticated = ref(false)

const checkAuth = async () => {
  try {
    const response = await api.get('/auth/user/')
    isAuthenticated.value = true
    userEmail.value = response.data.email
  } catch (error) {
    isAuthenticated.value = false
    userEmail.value = ''
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }
}

const login = async (email: string, password: string) => {
  const response = await api.post('/auth/login/', {
    username: email,
    password
  })
  
  localStorage.setItem('access_token', response.data.access)
  localStorage.setItem('refresh_token', response.data.refresh)
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
  const response = await api.post('/auth/register/', {
    email,
    password
  })
  
  localStorage.setItem('access_token', response.data.tokens.access)
  localStorage.setItem('refresh_token', response.data.tokens.refresh)
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