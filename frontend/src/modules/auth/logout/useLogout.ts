import { useRouter } from 'vue-router'
import { useAuthState } from '@/modules/backend-communication/api'
import { useToast } from '@/shared/elements/toast/useToast'

export const useLogout = () => {
  const router = useRouter()
  const { logout } = useAuthState()
  const { success } = useToast()

  const handleLogout = () => {
    logout()
    success('Successfully logged out')
    router.push({ name: 'login' })
  }

  return {
    handleLogout
  }
}
