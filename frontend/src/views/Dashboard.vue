<template>
  <main-layout>
    <div class="dashboard-container">
      <!-- Welcome Banner -->
      <div class="welcome-banner">
        <div class="welcome-content">
          <h1 class="welcome-title">Welcome back, {{ authStore.user?.full_name }}! 👋</h1>
          <p class="welcome-subtitle">Here's what's happening with your projects today</p>
        </div>
        <div class="welcome-illustration">
          <el-icon class="floating-icon" :size="120"><TrendCharts /></el-icon>
        </div>
      </div>

      <!-- Statistics Cards with Animation -->
      <el-row :gutter="24" class="stats-row">
        <el-col :span="6" v-for="(stat, index) in stats" :key="index">
          <el-card class="stat-card animate-slide-in" :style="{ 'animation-delay': `${index * 0.1}s` }">
            <div class="stat-content">
              <div class="stat-icon" :class="stat.class">
                <div class="icon-bg"></div>
                <el-icon :size="36"><component :is="stat.icon" /></el-icon>
              </div>
              <div class="stat-info">
                <p class="stat-label">{{ stat.label }}</p>
                <div class="stat-value-container">
                  <h2 class="stat-value">{{ stat.value }}</h2>
                  <span class="stat-trend" :class="stat.trend">
                    <el-icon><component :is="stat.trendIcon" /></el-icon>
                    {{ stat.trendValue }}
                  </span>
                </div>
                <div class="stat-progress">
                  <el-progress
                    :percentage="stat.percentage"
                    :stroke-width="6"
                    :show-text="false"
                    :color="stat.color"
                  />
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- Content Row -->
      <el-row :gutter="20">
        <el-col :span="16">
          <!-- Upcoming Tasks -->
          <el-card class="section-card">
            <template #header>
              <div class="card-header">
                <span>Upcoming Deadlines</span>
                <router-link to="/tasks">View All</router-link>
              </div>
            </template>
            
            <el-empty v-if="!overview?.upcoming_tasks?.length" description="No upcoming tasks" />
            
            <div v-else class="task-list">
              <div
                v-for="task in overview.upcoming_tasks"
                :key="task.id"
                class="task-item"
              >
                <div class="task-info">
                  <h4>{{ task.title }}</h4>
                  <p>Due: {{ formatDate(task.end_date) }}</p>
                </div>
                <el-tag :type="getPriorityType(task.priority)" size="small">
                  {{ task.priority }}
                </el-tag>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <!-- Recent Projects -->
          <el-card class="section-card">
            <template #header>
              <div class="card-header">
                <span>Recent Projects</span>
                <router-link to="/projects">View All</router-link>
              </div>
            </template>
            
            <el-empty v-if="!overview?.recent_projects?.length" description="No projects yet" />
            
            <div v-else class="project-list">
              <div
                v-for="project in overview.recent_projects"
                :key="project.id"
                class="project-item"
                @click="goToProject(project.id)"
              >
                <div class="project-color" :style="{ background: project.color }"></div>
                <div class="project-info">
                  <h4>{{ project.name }}</h4>
                  <p>{{ project.tasks_count }} tasks</p>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- Additional Dashboard Sections -->
      <el-row :gutter="20" style="margin-top: 20px;">
        <!-- Project Status Distribution -->
        <el-col :span="12">
          <el-card class="section-card">
            <template #header>
              <div class="card-header">
                <span>Project Status Distribution</span>
              </div>
            </template>
            <div class="status-distribution">
              <div class="status-item" v-for="status in projectStatusData" :key="status.name">
                <div class="status-header">
                  <span class="status-name">{{ status.name }}</span>
                  <span class="status-count">{{ status.count }}</span>
                </div>
                <el-progress
                  :percentage="status.percentage"
                  :color="status.color"
                  :stroke-width="12"
                />
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- Quick Actions -->
        <el-col :span="12">
          <el-card class="section-card">
            <template #header>
              <div class="card-header">
                <span>Quick Actions</span>
              </div>
            </template>
            <div class="quick-actions">
              <el-button
                type="primary"
                size="large"
                @click="router.push('/projects')"
                class="action-button"
              >
                <el-icon><FolderOpened /></el-icon>
                <span>Create New Project</span>
              </el-button>
              <el-button
                type="success"
                size="large"
                @click="router.push('/tasks')"
                class="action-button"
              >
                <el-icon><List /></el-icon>
                <span>View All Tasks</span>
              </el-button>
              <el-button
                type="warning"
                size="large"
                @click="router.push('/notifications')"
                class="action-button"
              >
                <el-icon><Bell /></el-icon>
                <span>Notifications</span>
              </el-button>
              <el-button
                type="info"
                size="large"
                @click="showReportsDialog = true"
                class="action-button"
              >
                <el-icon><Document /></el-icon>
                <span>Generate Report</span>
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- Reports Dialog -->
      <el-dialog v-model="showReportsDialog" title="Select Project for Report" width="500px">
        <div v-if="overview?.recent_projects?.length">
          <div
            v-for="project in overview.recent_projects"
            :key="project.id"
            class="report-project-item"
            @click="goToProjectReport(project.id)"
          >
            <div class="project-color" :style="{ background: project.color }"></div>
            <div class="project-info">
              <h4>{{ project.name }}</h4>
              <p>{{ project.tasks_count }} tasks</p>
            </div>
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
        <el-empty v-else description="No projects available" />
      </el-dialog>
    </div>
  </main-layout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import MainLayout from '@/components/Layout/MainLayout.vue'
import dashboardAPI from '@/services/api/dashboard'
import {
  FolderOpened,
  List,
  CircleCheck,
  Clock,
  TrendCharts,
  ArrowUp,
  ArrowDown,
  Bell,
  Document,
  ArrowRight
} from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const overview = ref(null)
const showReportsDialog = ref(false)

const stats = computed(() => [
  {
    label: 'Total Projects',
    value: overview.value?.projects?.total || 0,
    icon: FolderOpened,
    class: 'projects',
    color: '#667eea',
    trend: 'up',
    trendIcon: ArrowUp,
    trendValue: '+12%',
    percentage: 75
  },
  {
    label: 'Total Tasks',
    value: overview.value?.tasks?.total || 0,
    icon: List,
    class: 'tasks',
    color: '#67c23a',
    trend: 'up',
    trendIcon: ArrowUp,
    trendValue: '+8%',
    percentage: 60
  },
  {
    label: 'Completed',
    value: overview.value?.tasks?.completed || 0,
    icon: CircleCheck,
    class: 'completed',
    color: '#85ce61',
    trend: 'up',
    trendIcon: ArrowUp,
    trendValue: '+15%',
    percentage: 85
  },
  {
    label: 'In Progress',
    value: overview.value?.tasks?.in_progress || 0,
    icon: Clock,
    class: 'pending',
    color: '#409eff',
    trend: 'down',
    trendIcon: ArrowDown,
    trendValue: '-5%',
    percentage: 45
  }
])

const fetchOverview = async () => {
  try {
    const response = await dashboardAPI.getOverview()
    overview.value = response.data
  } catch (error) {
    console.error('Failed to fetch overview:', error)
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

const getPriorityType = (priority) => {
  const types = {
    low: 'info',
    medium: '',
    high: 'warning',
    critical: 'danger'
  }
  return types[priority] || ''
}

const projectStatusData = computed(() => {
  const projects = overview.value?.projects || {}
  const total = projects.total || 1
  
  return [
    {
      name: 'Planning',
      count: projects.planning || 0,
      percentage: Math.round((projects.planning || 0) / total * 100),
      color: '#909399'
    },
    {
      name: 'In Progress',
      count: projects.in_progress || 0,
      percentage: Math.round((projects.in_progress || 0) / total * 100),
      color: '#409eff'
    },
    {
      name: 'On Hold',
      count: projects.on_hold || 0,
      percentage: Math.round((projects.on_hold || 0) / total * 100),
      color: '#e6a23c'
    },
    {
      name: 'Completed',
      count: projects.completed || 0,
      percentage: Math.round((projects.completed || 0) / total * 100),
      color: '#67c23a'
    }
  ]
})

const goToProject = (id) => {
  router.push(`/projects/${id}`)
}

const goToProjectReport = (id) => {
  showReportsDialog.value = false
  router.push(`/projects/${id}/report`)
}

onMounted(() => {
  fetchOverview()
})
</script>

<style scoped>
.dashboard-container {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
  min-height: 100vh;
}

/* Welcome Banner */
.welcome-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 24px;
  padding: 40px;
  margin-bottom: 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
  position: relative;
  overflow: hidden;
}

.welcome-banner::before {
  content: '';
  position: absolute;
  width: 300px;
  height: 300px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  top: -100px;
  right: -100px;
}

.welcome-content {
  z-index: 1;
}

.welcome-title {
  color: white;
  font-size: 36px;
  font-weight: 700;
  margin: 0 0 12px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.welcome-subtitle {
  color: rgba(255, 255, 255, 0.9);
  font-size: 18px;
  margin: 0;
}

.welcome-illustration {
  z-index: 1;
}

.floating-icon {
  color: rgba(255, 255, 255, 0.3);
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(5deg); }
}

/* Statistics Cards */
.stats-row {
  margin-bottom: 32px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 20px;
  overflow: hidden;
  background: white;
  border: none;
  position: relative;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.stat-card:hover::before {
  transform: scaleX(1);
}

.stat-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.stat-content {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  padding: 8px;
}

.stat-icon {
  width: 80px;
  height: 80px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  color: white;
  position: relative;
  overflow: hidden;
  flex-shrink: 0;
}

.icon-bg {
  position: absolute;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  transform: scale(0);
  transition: transform 0.6s ease;
}

.stat-card:hover .icon-bg {
  transform: scale(2);
}

.stat-icon.projects { 
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
}
.stat-icon.tasks { 
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  box-shadow: 0 8px 24px rgba(103, 194, 58, 0.4);
}
.stat-icon.completed { 
  background: linear-gradient(135deg, #85ce61 0%, #67c23a 100%);
  box-shadow: 0 8px 24px rgba(133, 206, 97, 0.4);
}
.stat-icon.pending { 
  background: linear-gradient(135deg, #409eff 0%, #79bbff 100%);
  box-shadow: 0 8px 24px rgba(64, 158, 255, 0.4);
}

.stat-info {
  flex: 1;
  padding-top: 4px;
}

.stat-label {
  margin: 0 0 8px 0;
  font-size: 13px;
  color: #909399;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

.stat-value-container {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.stat-value {
  margin: 0;
  font-size: 36px;
  font-weight: 700;
  color: #303133;
  line-height: 1;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.stat-trend.up {
  background: #f0f9ff;
  color: #67c23a;
}

.stat-trend.down {
  background: #fef0f0;
  color: #f56c6c;
}

.stat-progress {
  margin-top: 8px;
}

.section-card {
  margin-bottom: 20px;
  height: 400px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header span {
  font-weight: 600;
  color: #303133;
}

.card-header a {
  color: #409eff;
  font-size: 14px;
  text-decoration: none;
}

.task-list {
  max-height: 320px;
  overflow-y: auto;
}

.task-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.task-item:last-child {
  border-bottom: none;
}

.task-info h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  color: #303133;
}

.task-info p {
  margin: 0;
  font-size: 12px;
  color: #909399;
}

.project-list {
  max-height: 320px;
  overflow-y: auto;
}

.project-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid #e4e7ed;
  cursor: pointer;
  transition: background 0.2s;
}

.project-item:hover {
  background: #f5f7fa;
}

.project-item:last-child {
  border-bottom: none;
}

.project-color {
  width: 40px;
  height: 40px;
  border-radius: 8px;
}

.project-info h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  color: #303133;
}

.project-info p {
  margin: 0;
  font-size: 12px;
  color: #909399;
}

/* Status Distribution */
.status-distribution {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 8px 0;
}

.status-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.status-count {
  font-size: 18px;
  font-weight: 700;
  color: #606266;
}

/* Quick Actions */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.quick-actions .action-button {
  width: 100% !important;
  height: 100px !important;
  display: inline-flex !important;
  flex-direction: row !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 12px;
  font-size: 16px !important;
  font-weight: 600;
  transition: all 0.3s;
  white-space: nowrap;
  padding: 0 24px !important;
  margin: 0 !important;
  border-radius: 12px;
  vertical-align: middle;
}

.quick-actions .action-button:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15) !important;
}

.quick-actions .action-button .el-icon {
  font-size: 28px !important;
  flex-shrink: 0;
  margin: 0 !important;
  line-height: 1;
}

.quick-actions .action-button span {
  line-height: 1;
  margin: 0 !important;
  display: inline-block;
}

/* Report Project Item */
.report-project-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.report-project-item:hover {
  background: #f5f7fa;
  border-color: #409eff;
  transform: translateX(4px);
}

.report-project-item .project-color {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  flex-shrink: 0;
}

.report-project-item .project-info {
  flex: 1;
}

.report-project-item .project-info h4 {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.report-project-item .project-info p {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

.report-project-item .el-icon {
  font-size: 20px;
  color: #909399;
  transition: all 0.3s;
}

.report-project-item:hover .el-icon {
  color: #409eff;
}
</style>

