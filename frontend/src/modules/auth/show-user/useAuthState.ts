import { ref, onMounted } from 'vue'
import api from '@/modules/auth/api'

export const useAuthState = () => {
  const isAuthenticated = ref(false)
  const userEmail = ref('')
  const isLoading = ref(true)
  const hasChecked = ref(false)

  const checkAuth = async () => {
    // Only check if we haven't checked yet
    if (hasChecked.value) return
    
    try {
      const response = await api.get('/auth/user/')
      isAuthenticated.value = true
      userEmail.value = response.data.email
    } catch (error) {
      isAuthenticated.value = false
      userEmail.value = ''
    } finally {
      isLoading.value = false
      hasChecked.value = true
    }
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    isAuthenticated.value = false
    userEmail.value = ''
    hasChecked.value = false // Reset so we can check again if needed
  }

  onMounted(() => {
    // Only check if we have a token
    if (localStorage.getItem('access_token')) {
      checkAuth()
    } else {
      isLoading.value = false
      hasChecked.value = true
    }
  })

  return {
    isAuthenticated,
    userEmail,
    isLoading,
    logout
  }
} 