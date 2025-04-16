<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { requestPasswordReset } from '@/modules/backend-communication/api'
import { handlePasswordReset } from './handlePasswordReset'
import { useToast } from '@/modules/elements/toast/useToast'

const route = useRoute()
const toast = useToast()

const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const isLoading = ref(false)
const error = ref<string | null>(null)

const isResetMode = computed(() => {
  return Boolean(route.query.uid && route.query.token)
})

const validatePassword = () => {
  if (password.value.length < 8) {
    return 'Password must be at least 8 characters long'
  }
  if (password.value !== confirmPassword.value) {
    return 'Passwords do not match'
  }
  return null
}

const handleSubmit = async () => {
  error.value = null
  
  if (isResetMode.value) {
    const passwordError = validatePassword()
    if (passwordError) {
      error.value = passwordError
      return
    }
    
    try {
      isLoading.value = true
      await handlePasswordReset(
        route.query.uid as string,
        route.query.token as string,
        password.value
      )
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'An error occurred'
    } finally {
      isLoading.value = false
    }
  } else {
    try {
      isLoading.value = true
      await requestPasswordReset(email.value)
      toast.success('If an account exists with this email, a password reset link has been sent.')
      email.value = ''
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'An error occurred'
    } finally {
      isLoading.value = false
    }
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-base-200">
    <div class="card w-96 bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl font-bold mb-4">
          {{ isResetMode ? 'Reset Password' : 'Request Password Reset' }}
        </h2>
        
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div v-if="!isResetMode" class="form-control">
            <label class="label">
              <span class="label-text">Email</span>
            </label>
            <input 
              type="email" 
              v-model="email" 
              placeholder="Enter your email" 
              class="input input-bordered w-full"
              required
            />
          </div>

          <template v-if="isResetMode">
            <div class="form-control">
              <label class="label">
                <span class="label-text">New Password</span>
              </label>
              <input 
                type="password" 
                v-model="password" 
                placeholder="Enter new password" 
                class="input input-bordered w-full"
                required
                minlength="8"
              />
            </div>

            <div class="form-control">
              <label class="label">
                <span class="label-text">Confirm Password</span>
              </label>
              <input 
                type="password" 
                v-model="confirmPassword" 
                placeholder="Confirm new password" 
                class="input input-bordered w-full"
                required
                minlength="8"
              />
            </div>
          </template>

          <div v-if="error" class="text-error text-sm">
            {{ error }}
          </div>

          <div class="card-actions justify-end mt-6">
            <button 
              type="submit" 
              class="btn btn-primary w-full"
              :disabled="isLoading"
            >
              {{ isLoading ? 'Processing...' : (isResetMode ? 'Reset Password' : 'Request Reset') }}
            </button>
          </div>
        </form>

        <div class="text-center mt-4">
          <p class="text-sm">
            Remember your password? 
            <router-link to="/login" class="link link-primary">Login here</router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
