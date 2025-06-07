import { createRouter, createWebHistory } from 'vue-router';

import App from '../App.vue';
import BasicLayout from '../layout/BasicLayout.vue';
import Login from '../views/Login.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: BasicLayout
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router; 