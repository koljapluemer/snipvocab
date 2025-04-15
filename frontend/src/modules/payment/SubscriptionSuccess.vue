<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/shared/elements/toast/useToast'

const router = useRouter()
const toast = useToast()

onMounted(() => {
  toast.success('Successfully subscribed to premium!')
  router.push({ name: 'home' })
})
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <div class="max-w-2xl mx-auto">
      <div class="bg-base-100 shadow-xl rounded-lg p-6">
        <h1 class="text-2xl font-bold mb-6">Subscription Successful</h1>
        <p class="text-base-content/80">Redirecting you to the home page...</p>
      </div>
    </div>
  </div>
</template> 