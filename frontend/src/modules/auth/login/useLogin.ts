import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/modules/auth/api'

export const useLogin = () => {
  const router = useRouter()
  const email = ref('')
  const password = ref('')
  const error = ref('')
  const isLoading = ref(false)

  const handleSubmit = async () => {
    try {
      isLoading.value = true
      error.value = ''
      
      const response = await api.post('/auth/login/', {
        username: email.value,
        password: password.value
      })

      // Store tokens in localStorage
      localStorage.setItem('access_token', response.data.access)
      localStorage.setItem('refresh_token', response.data.refresh)
      
      // Redirect to home page after successful login
      router.push('/')
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Login failed. Please check your credentials.'
    } finally {
      isLoading.value = false
    }
  }

  return {
    email,
    password,
    error,
    isLoading,
    handleSubmit
  }
}
