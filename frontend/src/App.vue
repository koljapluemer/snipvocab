<script setup lang="ts">
import ShowUserWidget from '@/modules/auth/show-user/ShowUserWidget.vue'
import ToastContainer from '@/modules/elements/toast/ToastContainer.vue'
import Footer from '@/components/Footer.vue'
</script>

<template>
  <header class="bg-base-100 shadow-sm">
    <nav class="container mx-auto px-4 py-2 flex justify-between items-center">
      <div class="flex gap-4">
        <router-link :to="{ name: 'landing' }" class="btn btn-ghost">AwV</router-link>
        <router-link :to="{ name: 'home' }" class="btn btn-ghost">Dashboard</router-link>
      </div>
      <ShowUserWidget />
    </nav>
  </header>
  
  <main class="container mx-auto my-4">
    <router-view></router-view>
    <ToastContainer />
  </main>

  <Footer />
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
