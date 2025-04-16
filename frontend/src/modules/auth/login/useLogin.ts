import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthState } from '@/modules/backend-communication/api'
import { useToast } from '@/shared/elements/toast/useToast'

export const useLogin = () => {
  const router = useRouter()
  const route = useRoute()
  const { login } = useAuthState()
  const { warning } = useToast()
  const email = ref('')
  const password = ref('')
  const error = ref('')
  const isLoading = ref(false)

  onMounted(() => {
    const message = route.query.message as string
    if (message) {
      warning(message)
    }
  })

  const handleSubmit = async () => {
    try {
      isLoading.value = true
      error.value = ''
      
      await login(email.value, password.value)
      
      // Redirect to the originally requested page if it exists
      const redirectPath = route.query.redirect as string
      if (redirectPath) {
        router.push(redirectPath)
      } else {
        router.push({ name: 'home' })
      }
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
