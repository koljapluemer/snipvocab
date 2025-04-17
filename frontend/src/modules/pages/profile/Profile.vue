<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { getUserInfo, createCheckoutSession, createCustomerPortalSession, getSubscriptionInfo, deleteUser } from '@/modules/backend-communication/api'
import { useRouter } from 'vue-router'
import type { UserInfoResponse, SubscriptionInfoResponse } from '@/modules/backend-communication/apiTypes'
import PremiumAdvantages from '@/modules/elements/premium-advantages/PremiumAdvantages.vue'

const router = useRouter()
const userInfo = ref<UserInfoResponse | null>(null)
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
    const [userResponse, subscriptionResponse] = await Promise.all([
      getUserInfo(),
      getSubscriptionInfo()
    ])

    userInfo.value = {
      ...userResponse,
      subscription: subscriptionResponse.subscription
    }
  } catch (err) {
    console.error('Error fetching user info:', err)
    error.value = err instanceof Error ? err.message : 'An error occurred'
  } finally {
    isLoading.value = false
  }
}

const handleManageSubscription = async () => {
  try {
    isLoading.value = true
    const { portalUrl } = await createCustomerPortalSession()
    window.location.href = portalUrl
  } catch (err) {
    console.error('Error accessing customer portal:', err)
    error.value = err instanceof Error ? err.message : 'Failed to access customer portal'
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

const handleDeleteAccount = async () => {
  if (!confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
    return
  }

  try {
    isLoading.value = true
    await deleteUser()
    // Clear auth state and redirect to home
    localStorage.clear()
    router.push('/')
  } catch (err) {
    console.error('Error deleting account:', err)
    error.value = err instanceof Error ? err.message : 'Failed to delete account'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchUserInfo()
})
</script>

<template>
  <div>
    <div v-if="isLoading" class="flex justify-center py-16">
      <div class="loading loading-spinner loading-lg"></div>
    </div>

    <div v-else-if="error" class="alert alert-error shadow-lg">
      <span>{{ error }}</span>
    </div>

    <div v-else class="bg-base-100 shadow-xl rounded-xl p-8">
      <h1 class="text-3xl font-bold text-primary mb-8 text-center">Profile</h1>

      <div class="mb-8">
        <div class="flex items-center gap-4 mb-6">
          <h2 class="text-2xl font-bold">Premium Subscription</h2>

          <span class="badge badge-lg" :class="{
            'badge-success': subscriptionStatus === 'active' && !isSubscriptionCanceling,
            'badge-error': subscriptionStatus === 'canceled' || isSubscriptionCanceling,
            'badge-warning': subscriptionStatus === 'Error fetching subscription details',
            'badge-info': subscriptionStatus === 'No subscription'
          }">
            {{ subscriptionStatus }}
          </span>
        </div>

        <div v-if="subscriptionExpiration" class="mb-6">
          <p v-if="isSubscriptionCanceling" class="text-warning">
            Your subscription will end on {{ subscriptionExpiration }}
          </p>
          <p v-else class="text-success">
            Your subscription will renew on {{ subscriptionExpiration }}
          </p>
        </div>

        <div class="flex flex-col items-center gap-8">
          <button v-if="userInfo?.subscription?.status === 'active'" 
            class="btn btn-primary btn-lg" 
            @click="handleManageSubscription" 
            :disabled="isLoading">
            Manage Subscription
          </button>

          <template v-else-if="!userInfo?.subscription">
            <PremiumAdvantages />
            <button class="btn btn-primary btn-lg" @click="handleSubscribe" :disabled="isLoading">
              Subscribe Now
            </button>
          </template>
        </div>
      </div>

      <div class="divider"></div>

      <div class="flex flex-col items-center gap-4 mb-8">
        <h2 class="text-2xl font-bold">Need Help?</h2>
        <div class="text-center">
          <p class="mb-2">Have questions, feedback, or need assistance?</p>
          <p class="text-primary font-medium">arabicwithvideos.contact@gmail.com</p>
          <a 
            href="mailto:arabicwithvideos.contact@gmail.com" 
            class="btn btn-ghost mt-4"
          >
            Contact Us
          </a>
        </div>
      </div>

      <div class="divider"></div>

      <div class="flex flex-col items-center gap-4">
        <h2 class="text-2xl font-bold text-error">Danger Zone</h2>
        <button 
          class="btn btn-error btn-lg" 
          @click="handleDeleteAccount" 
          :disabled="isLoading">
          Delete Account
        </button>
        <p class="text-sm text-error">This action cannot be undone. All your data will be permanently deleted.</p>
      </div>
    </div>
  </div>
</template>
