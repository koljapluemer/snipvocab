import { confirmPasswordReset } from '@/modules/backend-communication/api'
import { useToast } from '@/modules/elements/toast/useToast'
import router from '@/router'

export const handlePasswordReset = async (uid: string, token: string, password: string) => {
  const toast = useToast()
  
  try {
    await confirmPasswordReset(uid, token, password)
    toast.success('Password has been reset successfully')
    
    // Redirect to login if not already there
    if (router.currentRoute.value.name !== 'login') {
      router.push({ name: 'login' })
    }
  } catch (error) {
    toast.error(error instanceof Error ? error.message : 'Failed to reset password')
    throw error
  }
}
