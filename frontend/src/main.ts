import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router.ts'

// Initialize GoatCounter for SPA
window.goatcounter = {
  no_onload: true,
  count: () => {} // This will be replaced by the actual implementation when the script loads
}

const app = createApp(App)
app.use(router)
app.mount('#app')

// Track route changes
router.afterEach((to) => {
  if (window.goatcounter) {
    window.goatcounter.count({
      path: location.pathname + location.search + location.hash,
    })
  }
})
