<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from '@/modules/elements/toast/useToast'
import { confirmEmail } from '@/modules/backend-communication/api'

const route = useRoute()
const router = useRouter()
const toast = useToast()

onMounted(async () => {
  const uid = route.query.uid as string
  const token = route.query.token as string

  if (!uid || !token) {
    toast.error('Invalid confirmation link')
    router.push({ name: 'home' })
    return
  }

  try {
    await confirmEmail(uid, token)
    toast.success('Email confirmed successfully!')
    router.push({ name: 'home' })
  } catch (error) {
    toast.error('Failed to confirm email. Please try again.')
    router.push({ name: 'home' })
  }
})
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-base-200">
    <div class="card w-96 bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl font-bold mb-4">Confirming Email</h2>
        <p class="text-base-content/80">Please wait while we confirm your email...</p>
      </div>
    </div>
  </div>
</template>
