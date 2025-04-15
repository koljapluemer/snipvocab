<script setup lang="ts">
import { useAuthState } from '../useAuthState'
import LogoutButton from '../logout/LogoutButton.vue'

const auth = useAuthState()
</script>

<template>
  <div class="flex items-center gap-4">
    <div v-if="auth.isAuthenticated.value" class="flex items-center gap-2">
      <router-link :to="{ name: 'profile' }" class="btn btn-ghost btn-sm">
        <span class="text-sm">{{ auth.userEmail.value }}</span>
      </router-link>
      <LogoutButton />
    </div>

    <div v-else class="flex items-center gap-2">
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
    </div>
  </div>
</template>
