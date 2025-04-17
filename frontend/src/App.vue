<script setup lang="ts">
import ShowUserWidget from '@/modules/auth/show-user/ShowUserWidget.vue'
import ToastContainer from '@/modules/elements/toast/ToastContainer.vue'
</script>

<template>
  <div class="min-h-screen flex flex-col bg-base-100">
    <header class="bg-base-100 shadow-sm">
      <nav class="container mx-auto px-4 py-4 flex justify-between items-center">
        <div class="flex gap-4">
          <router-link :to="{ name: 'landing' }" class="btn btn-ghost text-xl font-bold">AwV</router-link>
          <router-link :to="{ name: 'home' }" class="btn btn-ghost text-lg">Dashboard</router-link>
          <router-link :to="{ name: 'premium' }" class="btn btn-ghost text-lg">Premium</router-link>
        </div>
        <ShowUserWidget />
      </nav>
    </header>
    
    <main class="container mx-auto px-4 py-8 flex-grow max-w-3xl">
      <router-view></router-view>
      <ToastContainer />
    </main>

    <footer class="footer footer-center p-10 bg-base-200 text-base-content">
      <nav>
        <div class="grid grid-flow-col gap-4">
          <router-link to="/terms" class="link link-hover">Terms</router-link>
          <router-link to="/privacy" class="link link-hover">Privacy</router-link>
          <a href="mailto:arabicwithvideos.contact@gmail.com" class="link link-hover">Contact</a>
        </div>
      </nav>
      <aside>
        <p>Copyright © {{ new Date().getFullYear() }} - Arabic With Videos</p>
      </aside>
    </footer>
  </div>
</template>

<style>
.toast > * {
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
