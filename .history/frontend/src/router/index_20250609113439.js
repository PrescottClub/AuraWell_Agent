import { createRouter, createWebHistory } from 'vue-router';

import App from '../App.vue';
import BasicLayout from '../layout/BasicLayout.vue';
import Login from '../views/Login.vue';
import AdminLayout from '../layout/AdminLayout.vue';
import Welcome from '../views/admin/Welcome.vue';

const routes = [
  {
    path: '/',
    component: BasicLayout,
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('../views/user/Home.vue')
      }
    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/admin',
    name: 'Admin',
    component: AdminLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Welcome',
        component: Welcome
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/admin/Dashboard.vue')
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('../views/admin/Users.vue')
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('../views/admin/Settings.vue')
      },
      {
        path: 'health-summary',
        name: 'HealthSummary',
        component: () => import('../views/admin/HealthSummary.vue')
      }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 路由守卫
router.beforeEach((to, from, next) => {
  const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
  
  if (to.meta.requiresAuth && !isLoggedIn) {
    next('/login');
  } else {
    next();
  }
});

export default router; 