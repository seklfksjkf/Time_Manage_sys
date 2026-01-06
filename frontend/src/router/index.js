import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/projects',
    name: 'Projects',
    component: () => import('@/views/projects/ProjectList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/projects/:id',
    name: 'ProjectDetail',
    component: () => import('@/views/projects/ProjectDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/projects/:id/timeline',
    name: 'ProjectTimeline',
    component: () => import('@/views/projects/ProjectTimeline.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/projects/:id/report',
    name: 'ProjectReport',
    component: () => import('@/views/projects/ProjectReport.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: () => import('@/views/tasks/TaskList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/notifications',
    name: 'Notifications',
    component: () => import('@/views/Notifications.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // Check if route requires authentication (default is true except for login/register)
  const requiresAuth = to.meta.requiresAuth !== false
  
  console.log('🔍 Navigation Guard:', {
    to: to.path,
    requiresAuth,
    isAuthenticated: authStore.isAuthenticated,
    token: !!authStore.token
  })

  if (requiresAuth && !authStore.isAuthenticated) {
    console.log('⛔ Not authenticated, redirecting to login')
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && authStore.isAuthenticated) {
    console.log('✅ Already authenticated, redirecting to dashboard')
    next('/dashboard')
  } else {
    console.log('✅ Navigation allowed')
    next()
  }
})

export default router

