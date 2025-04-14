import { ref } from 'vue'

export type ToastType = 'info' | 'success' | 'warning' | 'error'

interface Toast {
  id: string
  message: string
  type: ToastType
}

const toasts = ref<Toast[]>([])

export function useToast() {
  const addToast = (message: string, type: ToastType) => {
    const id = Math.random().toString(36).substring(2)
    toasts.value.push({ id, message, type })
  }

  const removeToast = (id: string) => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }

  return {
    toasts,
    removeToast,
    info: (message: string) => addToast(message, 'info'),
    success: (message: string) => addToast(message, 'success'),
    warning: (message: string) => addToast(message, 'warning'),
    error: (message: string) => addToast(message, 'error')
  }
} 