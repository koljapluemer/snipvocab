<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { getUserInfo, cancelSubscription, createCheckoutSession } from '@/modules/backend-communication/api'
import { useRouter } from 'vue-router'

const router = useRouter()
const userInfo = ref<{ email: string; id: number; subscription: { status: string | null; period_end?: number; cancel_at?: number; cancel_at_period_end?: boolean; error?: string } | null } | null>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)

const subscriptionStatus = computed(() => {
  if (!userInfo.value?.subscription) return 'No subscription'
  if (userInfo.value.subscription.error) return 'Error fetching subscription details'
  return userInfo.value.subscription.status
})

const subscriptionExpiration = computed(() => {
  if (!userInfo.value?.subscription) return null
  
  // If subscription is being canceled, use cancel_at if available, otherwise use period_end
  const timestamp = userInfo.value.subscription.cancel_at || userInfo.value.subscription.period_end
  if (!timestamp) return null
  
  const date = new Date(timestamp * 1000)
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})

const isSubscriptionCanceling = computed(() => {
  return userInfo.value?.subscription?.cancel_at_period_end === true || 
         (userInfo.value?.subscription?.cancel_at !== undefined && 
          userInfo.value?.subscription?.cancel_at !== null)
})

const fetchUserInfo = async () => {
  try {
    isLoading.value = true
    const response = await getUserInfo()
    console.log('User info response:', response)
    userInfo.value = response
    console.log('Current subscription status:', userInfo.value?.subscription?.status)
  } catch (err) {
    console.error('Error fetching user info:', err)
    error.value = err instanceof Error ? err.message : 'An error occurred'
  } finally {
    isLoading.value = false
  }
}

const handleCancelSubscription = async () => {
  try {
    isLoading.value = true
    await cancelSubscription()
    await fetchUserInfo() // Refresh user info to get updated subscription status
  } catch (err) {
    console.error('Error canceling subscription:', err)
    error.value = err instanceof Error ? err.message : 'Failed to cancel subscription'
  } finally {
    isLoading.value = false
  }
}

const handleSubscribe = async () => {
  try {
    isLoading.value = true
    error.value = null

    const { checkoutUrl } = await createCheckoutSession()
    window.location.href = checkoutUrl
  } catch (err) {
    console.error('Error creating checkout session:', err)
    error.value = err instanceof Error ? err.message : 'Failed to create checkout session. Please try again.'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  console.log('Profile component mounted')
  fetchUserInfo()
})
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <div class="max-w-2xl mx-auto">
      <div v-if="isLoading" class="flex justify-center">
        <div class="loading loading-spinner loading-lg"></div>
      </div>

      <div v-else-if="error" class="alert alert-error">
        <span>{{ error }}</span>
      </div>

      <div v-else class="bg-base-100 shadow-xl rounded-lg p-6">
        <h1 class="text-2xl font-bold mb-6">Profile</h1>

        <div class="mb-6">
          <div class="flex items-center gap-4 mb-4">
            <h2 class="text-xl font-semibold mb-2">Subscription</h2>

            <span class="badge" :class="{
              'badge-success': subscriptionStatus === 'active' && !isSubscriptionCanceling,
              'badge-error': subscriptionStatus === 'canceled' || isSubscriptionCanceling,
              'badge-warning': !subscriptionStatus || subscriptionStatus === 'Error fetching subscription details'
            }">
              {{ subscriptionStatus }}
            </span>
          </div>

          <div v-if="subscriptionExpiration" class="mb-4">
            <p v-if="isSubscriptionCanceling" class="text-warning">
              Your subscription will end on {{ subscriptionExpiration }}
            </p>
            <p v-else class="text-success">
              Your subscription will renew on {{ subscriptionExpiration }}
            </p>
          </div>

          <button v-if="userInfo?.subscription?.status === 'active' && !isSubscriptionCanceling" 
            class="btn btn-error" @click="handleCancelSubscription" :disabled="isLoading">
            Cancel Subscription
          </button>

          <button v-else-if="!userInfo?.subscription?.status" 
            class="btn btn-primary" @click="handleSubscribe" :disabled="isLoading">
            Subscribe Now
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
