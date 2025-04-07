<script setup lang="ts">
import { useRegister } from './useRegister'

const {
  email,
  password,
  confirmPassword,
  error,
  isLoading,
  handleSubmit
} = useRegister()
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-base-200">
    <div class="card w-96 bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl font-bold mb-4">Create an Account</h2>
        
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

          <div class="form-control">
            <label class="label">
              <span class="label-text">Confirm Password</span>
            </label>
            <input 
              type="password" 
              v-model="confirmPassword" 
              placeholder="Confirm your password" 
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
              {{ isLoading ? 'Registering...' : 'Register' }}
            </button>
          </div>
        </form>

        <div class="text-center mt-4">
          <p class="text-sm">
            Already have an account? 
            <router-link to="/login" class="link link-primary">Login here</router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
