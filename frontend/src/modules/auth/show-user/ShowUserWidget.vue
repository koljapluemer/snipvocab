<script setup lang="ts">
import { useAuthState } from './useAuthState'
import { useRouter } from 'vue-router'

const router = useRouter()
const {
  isAuthenticated,
  userEmail,
  isLoading,
  logout
} = useAuthState()

const handleLogout = () => {
  logout()
  router.push({ name: 'home' })
}
</script>

<template>
  <div class="flex items-center gap-4">
    <div v-if="isLoading" class="loading loading-spinner loading-sm"></div>
    
    <template v-else-if="isAuthenticated">
      <div class="flex items-center gap-2">
        <span class="text-sm">{{ userEmail }}</span>
        <button 
          @click="handleLogout" 
          class="btn btn-ghost btn-sm"
        >
          Logout
        </button>
      </div>
    </template>

    <template v-else>
      <router-link 
        :to="{ name: 'login' }" 
        class="btn btn-ghost btn-sm"
      >
        Login
      </router-link>
      <router-link 
        :to="{ name: 'register' }" 
        class="btn btn-primary btn-sm"
      >
        Register
      </router-link>
    </template>
  </div>
</template>
