<template>
  <main-layout>
    <div class="container">
      <div class="page-header">
        <h2 class="page-title">Notifications</h2>
        <el-button @click="markAllRead" :disabled="!hasUnread">
          Mark All as Read
        </el-button>
      </div>

      <el-card>
        <div v-if="notifications.length === 0" class="empty-state">
          <el-icon class="empty-state-icon"><Bell /></el-icon>
          <p class="empty-state-text">No notifications</p>
        </div>

        <div v-else class="notification-list">
          <div
            v-for="notification in notifications"
            :key="notification.id"
            class="notification-item"
            :class="{ unread: !notification.is_read }"
            @click="handleNotificationClick(notification)"
          >
            <div class="notification-icon" :class="`type-${notification.type}`">
              <el-icon v-if="notification.type === 'task_assigned'"><List /></el-icon>
              <el-icon v-else-if="notification.type === 'deadline_alert'"><Warning /></el-icon>
              <el-icon v-else-if="notification.type === 'project_update'"><FolderOpened /></el-icon>
              <el-icon v-else><Bell /></el-icon>
            </div>
            
            <div class="notification-content">
              <h4>{{ notification.title }}</h4>
              <p>{{ notification.message }}</p>
              <span class="notification-time">{{ formatTime(notification.created_at) }}</span>
            </div>
            
            <el-button
              v-if="!notification.is_read"
              type="primary"
              size="small"
              circle
              @click.stop="markRead(notification.id)"
            >
              <el-icon><Check /></el-icon>
            </el-button>
          </div>
        </div>
      </el-card>
    </div>
  </main-layout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import MainLayout from '@/components/Layout/MainLayout.vue'
import notificationAPI from '@/services/api/notifications'
import { ElMessage } from 'element-plus'
import {
  Bell,
  List,
  Warning,
  FolderOpened,
  Check
} from '@element-plus/icons-vue'

const notifications = ref([])

const hasUnread = computed(() => {
  return notifications.value.some(n => !n.is_read)
})

const fetchNotifications = async () => {
  try {
    const response = await notificationAPI.getAll()
    notifications.value = response.data.notifications
  } catch (error) {
    ElMessage.error('Failed to load notifications')
  }
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  
  const minutes = Math.floor(diff / 60000)
  if (minutes < 60) return `${minutes}m ago`
  
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days}d ago`
  
  return date.toLocaleDateString()
}

const markRead = async (id) => {
  try {
    await notificationAPI.markAsRead(id)
    const notification = notifications.value.find(n => n.id === id)
    if (notification) notification.is_read = true
  } catch (error) {
    ElMessage.error('Failed to mark as read')
  }
}

const markAllRead = async () => {
  try {
    await notificationAPI.markAllAsRead()
    notifications.value.forEach(n => n.is_read = true)
    ElMessage.success('All notifications marked as read')
  } catch (error) {
    ElMessage.error('Failed to mark all as read')
  }
}

const handleNotificationClick = (notification) => {
  if (!notification.is_read) {
    markRead(notification.id)
  }
}

onMounted(() => {
  fetchNotifications()
})
</script>

<style scoped>
.notification-list {
  max-height: 600px;
  overflow-y: auto;
}

.notification-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
  cursor: pointer;
  transition: background 0.2s;
}

.notification-item:hover {
  background: #f5f7fa;
}

.notification-item.unread {
  background: #ecf5ff;
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
}

.notification-icon.type-task_assigned { background: #409eff; }
.notification-icon.type-deadline_alert { background: #f56c6c; }
.notification-icon.type-project_update { background: #67c23a; }
.notification-icon.type-milestone_reached { background: #e6a23c; }

.notification-content {
  flex: 1;
}

.notification-content h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  color: #303133;
}

.notification-content p {
  margin: 0 0 4px 0;
  font-size: 13px;
  color: #606266;
}

.notification-time {
  font-size: 12px;
  color: #909399;
}
</style>

