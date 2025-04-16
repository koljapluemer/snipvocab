<template>
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
</template>

<script setup lang="ts">
// No additional logic needed
</script> 