<script setup lang="ts">
import { useLogin } from './useLogin'

const {
  email,
  password,
  error,
  isLoading,
  handleSubmit
} = useLogin()
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-base-200">
    <div class="card w-96 bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl font-bold mb-4">Login to Your Account</h2>
        
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div class="form-control">
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

          <div class="form-control">
            <label class="label">
              <span class="label-text">Password</span>
            </label>
            <input 
              type="password" 
              v-model="password" 
              placeholder="Enter your password" 
              class="input input-bordered w-full"
              required
            />
          </div>

          <div v-if="error" class="text-error text-sm">
            {{ error }}
          </div>

          <div class="card-actions justify-end mt-6">
            <button 
              type="submit" 
              class="btn btn-primary w-full"
              :disabled="isLoading"
            >
              {{ isLoading ? 'Logging in...' : 'Login' }}
            </button>
          </div>
        </form>

        <div class="text-center mt-4">
          <p class="text-sm">
            Don't have an account? 
            <router-link to="/register" class="link link-primary">Register here</router-link>
          </p>
          <p class="text-sm mt-2">
            <router-link to="/reset-password" class="link link-primary">Forgot your password?</router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
