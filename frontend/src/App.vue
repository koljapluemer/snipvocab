<script setup lang="ts">
import ShowUserWidget from '@/modules/auth/show-user/ShowUserWidget.vue'
import { useToast } from '@/shared/composables/useToast'

const toast = useToast()
</script>

<template>
  <header class="bg-base-100 shadow-sm">
    <nav class="container mx-auto px-4 py-2 flex justify-between items-center">
      <div class="flex gap-4">
        <router-link :to="{ name: 'home' }" class="btn btn-ghost">Home</router-link>
      </div>
      <ShowUserWidget />
    </nav>
  </header>
  <main class="container mx-auto px-4 py-8">
    <router-view></router-view>
    <!-- Toast -->
    <div class="toast toast-top toast-end">
      <div v-if="toast.show" :class="['alert', `alert-${toast.type}`]">
        <span>{{ toast.message }}</span>
      </div>
    </div>
  </main>
</template>
