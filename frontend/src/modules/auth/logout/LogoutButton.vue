<script setup lang="ts">
import { useLogout } from './useLogout'

const { handleLogout } = useLogout()
</script>

<template>
  <button 
    @click="handleLogout" 
    class="btn btn-ghost"
  >
    Logout
  </button>
</template>
