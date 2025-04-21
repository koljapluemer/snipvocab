import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router.ts'
import { useGoatCounter } from './useGoatCounter.ts'

const app = createApp(App)
app.use(router)
app.mount('#app')

// Initialize GoatCounter
useGoatCounter()
