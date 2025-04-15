<script setup lang="ts">
import { ref } from 'vue'
import { createCheckoutSession } from '@/modules/backend-communication/api'

const isLoading = ref(false)
const error = ref<string | null>(null)

const handleSubscribe = async () => {
  try {
    isLoading.value = true
    error.value = null
    
    const { sessionId } = await createCheckoutSession()
    
    // Redirect to Stripe Checkout
    window.location.href = `https://checkout.stripe.com/pay/${sessionId}`
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to create checkout session. Please try again.'
    console.error('Subscription error:', err)
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <div class="max-w-2xl mx-auto">
      <div class="bg-base-100 shadow-xl rounded-lg p-6">
        <h1 class="text-2xl font-bold mb-6">Profile</h1>
        
        <div class="mb-6">
          <h2 class="text-xl font-semibold mb-2">Subscription</h2>
          <p class="text-base-content/80 mb-4">Upgrade to premium to unlock all features!</p>
          
          <button 
            @click="handleSubscribe"
            class="btn btn-primary"
            :disabled="isLoading"
          >
            {{ isLoading ? 'Loading...' : 'Subscribe Now' }}
          </button>
          
          <p v-if="error" class="text-error mt-2">{{ error }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
