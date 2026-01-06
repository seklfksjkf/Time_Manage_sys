<template>
  <el-container class="main-layout">
    <el-aside width="200px">
      <div class="logo">
        <h2>TMS</h2>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        class="sidebar-menu"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <span>Dashboard</span>
        </el-menu-item>
        <el-menu-item index="/projects">
          <el-icon><FolderOpened /></el-icon>
          <span>Projects</span>
        </el-menu-item>
        <el-menu-item index="/tasks">
          <el-icon><List /></el-icon>
          <span>My Tasks</span>
        </el-menu-item>
        <el-menu-item index="/notifications">
          <el-badge :value="unreadCount" :hidden="unreadCount === 0">
            <el-icon><Bell /></el-icon>
          </el-badge>
          <span style="margin-left: 8px">Notifications</span>
        </el-menu-item>
        <el-menu-item index="/profile">
          <el-icon><User /></el-icon>
          <span>Profile</span>
        </el-menu-item>
      </el-menu>
      
      <div class="sidebar-footer">
        <el-button @click="handleLogout" text>
          <el-icon><SwitchButton /></el-icon>
          Logout
        </el-button>
      </div>
    </el-aside>

    <el-container>
      <el-header>
        <div class="header-left">
          <h3>{{ pageTitle }}</h3>
        </div>
        <div class="header-right">
          <span class="user-name">{{ authStore.user?.full_name }}</span>
          <el-avatar :size="36">{{ userInitials }}</el-avatar>
        </div>
      </el-header>

      <el-main>
        <slot />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import notificationAPI from '@/services/api/notifications'
import {
  Odometer,
  FolderOpened,
  List,
  Bell,
  User,
  SwitchButton
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const unreadCount = ref(0)

const activeMenu = computed(() => route.path)

const pageTitle = computed(() => {
  const titles = {
    '/dashboard': 'Dashboard',
    '/projects': 'Projects',
    '/tasks': 'My Tasks',
    '/notifications': 'Notifications',
    '/profile': 'Profile'
  }
  return titles[route.path] || 'Time Management System'
})

const userInitials = computed(() => {
  if (!authStore.user?.full_name) return 'U'
  const names = authStore.user.full_name.split(' ')
  return names.map(n => n[0]).join('').toUpperCase().slice(0, 2)
})

const fetchUnreadCount = async () => {
  try {
    const response = await notificationAPI.getUnreadCount()
    unreadCount.value = response.data.unread_count
  } catch (error) {
    console.error('Failed to fetch unread count:', error)
  }
}

const handleLogout = () => {
  authStore.logout()
  ElMessage.success('Logged out successfully')
  router.push('/login')
}

onMounted(() => {
  fetchUnreadCount()
  // Poll for notifications every 30 seconds
  setInterval(fetchUnreadCount, 30000)
})
</script>

<style scoped>
.main-layout {
  height: 100vh;
}

.el-aside {
  background: linear-gradient(180deg, #2c3e50 0%, #1a252f 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 100;
}

.el-aside::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 1px;
  height: 100%;
  background: linear-gradient(180deg, transparent, rgba(255, 255, 255, 0.1), transparent);
}

.logo {
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  position: relative;
}

.logo::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 20px;
  right: 20px;
  height: 2px;
  background: linear-gradient(90deg, transparent, #667eea, transparent);
}

.logo h2 {
  color: #fff;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: 2px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  background: linear-gradient(135deg, #fff 0%, #667eea 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.sidebar-menu {
  flex: 1;
  border: none;
  background: transparent;
  padding: 16px 0;
}

:deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.7);
  margin: 4px 12px;
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

:deep(.el-menu-item::before) {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(180deg, #667eea, #764ba2);
  transform: scaleY(0);
  transition: transform 0.3s ease;
  border-radius: 0 4px 4px 0;
}

:deep(.el-menu-item:hover::before),
:deep(.el-menu-item.is-active::before) {
  transform: scaleY(1);
}

:deep(.el-menu-item:hover),
:deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, 
    rgba(102, 126, 234, 0.2) 0%,
    rgba(118, 75, 162, 0.1) 100%
  );
  color: #fff;
}

:deep(.el-menu-item.is-active) {
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

:deep(.el-badge) {
  vertical-align: middle;
}

:deep(.el-badge__content) {
  background: linear-gradient(135deg, #f56c6c, #f89898);
  border: 2px solid #2c3e50;
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.sidebar-footer .el-button {
  width: 100%;
  color: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.sidebar-footer .el-button:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  transform: translateY(-2px);
}

.el-header {
  background: white;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  position: relative;
  z-index: 99;
}

.header-left h3 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.5px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-name {
  color: #606266;
  font-size: 14px;
  font-weight: 600;
}

:deep(.el-avatar) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  cursor: pointer;
  transition: all 0.3s ease;
}

:deep(.el-avatar:hover) {
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.el-main {
  background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
  overflow-y: auto;
}
</style>

