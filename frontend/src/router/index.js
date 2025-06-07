import { createRouter, createWebHistory } from 'vue-router';

import App from '../App.vue';
import BasicLayout from '../layout/BasicLayout.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: BasicLayout
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router; 