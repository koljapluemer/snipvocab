import { createRouter, createWebHistory } from 'vue-router'
import Register from '@/modules/auth/register/Register.vue'
import Login from '@/modules/auth/login/Login.vue'
import VideoView from '@/modules/videos/view-video/VideoView.vue'
import { useToast } from '@/modules/elements/toast/useToast'
import Dashboard from '@/modules/pages/dashboard/Dashboard.vue'
import SubscriptionSuccess from '@/modules/payment/SubscriptionSuccess.vue'
import Profile from '@/modules/pages/profile/Profile.vue'
import { useAuthState } from '@/modules/backend-communication/api'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Dashboard,
      meta: { requiresAuth: true }
    },
    {
      path: '/register',
      name: 'register',
      component: Register,
      meta: { requiresGuest: true }
    },
    {
      path: '/login',
      name: 'login',
      component: Login,
      meta: { requiresGuest: true }
    },
    {
      path: '/video/:videoId',
      name: 'video',
      component: VideoView,
      meta: { requiresAuth: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: Profile,
      meta: { requiresAuth: true }
    },
    {
      path: '/subscription/success',
      name: 'subscription-success',
      component: SubscriptionSuccess,
      meta: { requiresAuth: true }
    }
  ]
})

// Navigation guard
router.beforeEach(async (to, from, next) => {
  const { isAuthenticated, isLoading, isInitialized, checkAuth } = useAuthState()
  const toast = useToast()

  // Wait for auth to be initialized
  if (!isInitialized.value) {
    await checkAuth()
  }

  // Handle protected routes
  if (to.meta.requiresAuth && !isAuthenticated.value) {
    toast.warning('Please login to access this page')
    next({ 
      name: 'login', 
      query: { redirect: to.fullPath }
    })
    return
  }

  // Handle guest-only routes
  if (to.meta.requiresGuest && isAuthenticated.value) {
    toast.warning('You are already logged in')
    next({ name: 'home' })
    return
  }

  next()
})

export default router 