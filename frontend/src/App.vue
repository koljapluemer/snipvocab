<script setup lang="ts">
import ShowUserWidget from '@/modules/auth/show-user/ShowUserWidget.vue'
import ToastContainer from '@/modules/elements/toast/ToastContainer.vue'
import { useAuthState } from '@/modules/backend-communication/api'
const { isAuthenticated } = useAuthState()
</script>

<template>
  <div class="min-h-screen flex flex-col bg-base-100">
    <header class="bg-base-100 shadow-sm flex flex-row gap-2 justify-between items-center p-4">
      <router-link :to="{ name: 'landing' }" class="btn btn-ghost text-xl font-bold">
        <img src="/logo.png" class="w-8 h-8 mr-2" />
        <span class="hidden md:block">
          Arabic With Videos
        </span>
        <span class="badge badge-outline hidden md:block">Beta</span>

      </router-link>
      <nav class="flex justify-between items-center">

        <router-link v-if="isAuthenticated" :to="{ name: 'home' }" class="btn btn-ghost">Dashboard</router-link>
        <router-link v-if="isAuthenticated" :to="{ name: 'premium' }" class="btn btn-ghost">Premium</router-link>
        <ShowUserWidget class="hidden md:block" />
        <!-- link to profile on mobile -->
        <router-link v-if="isAuthenticated" :to="{ name: 'profile' }" class="btn btn-ghost md:hidden">
          Account
        </router-link>
      </nav>
    </header>

    <main class="container mx-auto px-4 py-8 flex-grow max-w-3xl">
      <router-view></router-view>
      <ToastContainer />
    </main>

    <footer class="flex flex-col gap-1 footer p-10 bg-base-200 text-base-content">
      <nav class="grid grid-flow-col gap-4">
        <router-link to="/terms" class="link link-hover">Terms</router-link>
        <router-link to="/privacy" class="link link-hover">Privacy</router-link>
        <a href="mailto:arabicwithvideos.contact@gmail.com" class="link link-hover">Contact</a>
      </nav>

      <p>Copyright © {{ new Date().getFullYear() }} - Arabic With Videos</p>

      <p class="text-sm">
        This is an early version of the app. We are still working on it. If there's any issues, please contact us.
      </p>
    </footer>
  </div>
</template>

<style>
.toast>* {
  animation: toast-pop 0.25s ease-out;
}

@keyframes toast-pop {
  0% {
    transform: scale(0.9);
    opacity: 0;
  }

  100% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
