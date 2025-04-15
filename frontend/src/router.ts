import { createRouter, createWebHistory } from 'vue-router'
import Register from '@/modules/auth/register/Register.vue'
import Login from '@/modules/auth/login/Login.vue'
import VideoView from '@/modules/videos/view-video/VideoView.vue'
import { useAuthState } from '@/modules/auth/useAuthState'
import { useToast } from '@/shared/elements/toast/useToast'
import Dashboard from './modules/pages/Dashboard.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Dashboard
    },
    {
      path: '/register',
      name: 'register',
      component: Register
    },
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      path: '/video/:videoId',
      name: 'video',
      component: VideoView,
      meta: {
        requiresAuth: true
      }
    }
  ]
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const { isAuthenticated } = useAuthState()
  const toast = useToast()

  if (to.meta.requiresAuth && !isAuthenticated.value) {
    toast.warning('Please login to access this page')
    next({ 
      name: 'login', 
      query: { redirect: to.fullPath }
    })
    return
  }
  next()
})

export default router 