import { ref } from 'vue'

export type ToastType = 'info' | 'success' | 'warning' | 'error'

interface ToastOptions {
  type?: ToastType
  duration?: number
}

export function useToast() {
  const show = ref(false)
  const message = ref('')
  const type = ref<ToastType>('info')

  const toast = (msg: string, options: ToastOptions = {}) => {
    message.value = msg
    type.value = options.type || 'info'
    show.value = true

    setTimeout(() => {
      show.value = false
    }, options.duration || 3000)
  }

  return {
    show,
    message,
    type,
    info: (msg: string) => toast(msg, { type: 'info' }),
    success: (msg: string) => toast(msg, { type: 'success' }),
    warning: (msg: string) => toast(msg, { type: 'warning' }),
    error: (msg: string) => toast(msg, { type: 'error' })
  }
} 