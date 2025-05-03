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

// Set dynamic title and description based on VITE_APP_LANG
type LangConfig = {
  title: string;
  description: string;
};

const langConfigs: Record<string, LangConfig> = {
  AR: {
    title: 'Arabic with Videos',
    description: 'Arabic with Videos is a platform for learning Arabic with Youtube videos.'
  },
  DE: {
    title: 'German with Videos',
    description: 'German with Videos is a platform for learning German with Youtube videos.'
  }
};

const lang = import.meta.env.VITE_APP_LANG as 'AR' | 'DE';
const config = langConfigs[lang] || langConfigs['AR'];
document.title = config.title;
const descTag = document.querySelector('meta[name="description"]');
if (descTag) descTag.setAttribute('content', config.description);
