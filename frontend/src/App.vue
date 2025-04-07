<script setup lang="ts">
</script>

<template>
  <header>
    <nav class="flex flex-row gap-1">
      <router-link to="/">Home</router-link>
      <router-link to="/register">Register</router-link>
      <router-link to="/login">Login</router-link>
    </nav>
  </header>
  <router-view></router-view>
</template>
