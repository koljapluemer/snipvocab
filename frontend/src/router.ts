import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/modules/misc-pages/home/HomeView.vue'
import Register from '@/modules/auth/register/Register.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/register',
      name: 'register',
      component: Register
    }
  ]
})

export default router 