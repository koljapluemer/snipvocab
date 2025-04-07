import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthState } from '../useAuthState'

export const useLogin = () => {
  const router = useRouter()
  const { login } = useAuthState()
  const email = ref('')
  const password = ref('')
  const error = ref('')
  const isLoading = ref(false)

  const handleSubmit = async () => {
    try {
      isLoading.value = true
      error.value = ''
      
      await login(email.value, password.value)
      router.push({ name: 'home' })
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
