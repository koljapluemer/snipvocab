<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getUserInfo, createCheckoutSession, createCustomerPortalSession, getSubscriptionInfo } from '@/modules/backend-communication/api'
import { useRouter } from 'vue-router'
import type { UserInfoResponse } from '@/modules/backend-communication/apiTypes'
import PremiumAdvantages from '@/modules/elements/premium-advantages/PremiumAdvantages.vue'

const router = useRouter()
const userInfo = ref<UserInfoResponse | null>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)

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

        <div v-else class="bg-base-100 shadow-xl rounded-xl p-8 flex flex-col items-center">
            <h1 class="text-3xl font-bold text-primary mb-8 text-center">Get Premium</h1>

            <div v-if="userInfo?.subscription?.status === 'active'">
                You are already a premium user. <br>
                <button class="btn btn-primary btn-lg" @click="handleManageSubscription" :disabled="isLoading">
                    Manage Subscription
                </button>
            </div>

            <template v-else-if="!userInfo?.subscription">
                <PremiumAdvantages />
                <button class="btn btn-primary btn-lg" @click="handleSubscribe" :disabled="isLoading">
                    Subscribe Now
                </button>
            </template>

            <div class="divider"></div>

            <div class="flex flex-col items-center gap-4">
                <h2 class="text-2xl font-bold">Need Help?</h2>
                <div class="text-center">
                    <p class="mb-2">Have questions about premium features or need assistance?</p>
                    <p class="text-primary font-medium">arabicwithvideos.contact@gmail.com</p>
                    <a 
                        href="mailto:arabicwithvideos.contact@gmail.com" 
                        class="btn btn-ghost mt-4"
                    >
                        Contact Us
                    </a>
                </div>
            </div>
        </div>
    </div>
</template>
