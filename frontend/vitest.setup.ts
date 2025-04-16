import { config } from '@vue/test-utils';
import { createRouter, createWebHistory } from 'vue-router';

// Mock router
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/video/:videoId',
      name: 'video',
      component: { template: '<div>Mock Video Component</div>' }
    }
  ]
});

// Set global router for tests
config.global.plugins = [router]; 