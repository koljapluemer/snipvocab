import { useRouter } from 'vue-router'
import { useAuthState } from '@/modules/backend-communication/api'

export const useLogout = () => {
  const router = useRouter()
  const { logout } = useAuthState()

  const handleLogout = () => {
    logout()
    if (router.currentRoute.value.name !== 'home') {
      router.push({ name: 'home' })
    }
  }

  return {
    handleLogout
  }
}
