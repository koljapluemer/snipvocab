<script setup lang="ts">
import { onMounted } from 'vue'
import type { ToastType } from './useToast'

const props = defineProps<{
  id: string
  message: string
  type: ToastType
  onRemove: (id: string) => void
}>()

onMounted(() => {
  setTimeout(() => props.onRemove(props.id), 3000)
})
</script>

<template>
  <div 
    @click="() => onRemove(id)"
    class="alert shadow-lg cursor-pointer"
    :class="{
      'alert-info': type === 'info',
      'alert-success': type === 'success',
      'alert-warning': type === 'warning',
      'alert-error': type === 'error'
    }"
  >
    {{ message }}
  </div>
</template>
