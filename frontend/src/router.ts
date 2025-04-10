import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/modules/misc-pages/home/HomeView.vue'
import Register from '@/modules/auth/register/Register.vue'
import Login from '@/modules/auth/login/Login.vue'
import VideoView from '@/modules/videos/view-video/VideoView.vue'
import SnippetView from './modules/snippets/view-snippet/SnippetView.vue'

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
    },
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      path: '/video/:videoId',
      name: 'video',
      component: VideoView
    },
    {
      path: '/snippet/:videoId/:index',
      name: 'snippet',
      component: SnippetView
    }
  ]
})

export default router 