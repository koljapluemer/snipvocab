import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthState } from '@/modules/backend-communication/api'

export const useRegister = () => {
  const router = useRouter()
  const { register } = useAuthState()
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
      
      await register(email.value, password.value)
      router.push({ name: 'home' })
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
