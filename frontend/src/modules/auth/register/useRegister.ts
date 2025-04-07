import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/modules/auth/api'

export const useRegister = () => {
  const router = useRouter()
  const email = ref('')
  const password = ref('')
  const confirmPassword = ref('')
  const error = ref('')
  const isLoading = ref(false)

  const handleSubmit = async () => {
    if (password.value !== confirmPassword.value) {
      error.value = 'Passwords do not match'
      return
    }

    try {
      isLoading.value = true
      error.value = ''
      
      const response = await api.post('/auth/register/', {
        email: email.value,
        password: password.value
      })

      // Store tokens in localStorage
      localStorage.setItem('access_token', response.data.tokens.access)
      localStorage.setItem('refresh_token', response.data.tokens.refresh)
      
      // Redirect to home page after successful registration
      router.push('/')
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Registration failed. Please try again.'
    } finally {
      isLoading.value = false
    }
  }

  return {
    email,
    password,
    confirmPassword,
    error,
    isLoading,
    handleSubmit
  }
}
