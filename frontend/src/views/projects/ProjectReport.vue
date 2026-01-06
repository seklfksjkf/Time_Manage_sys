<template>
  <div class="project-report">
    <div class="report-header">
      <el-button @click="$router.back()" text>
        <el-icon><ArrowLeft /></el-icon>
        Back
      </el-button>
      <h2 class="page-title">{{ project?.name }} - Progress Report</h2>
      <div class="header-actions">
        <el-button @click="fetchReport" :loading="loading">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
        <el-dropdown @command="handleExport" trigger="click">
          <el-button type="primary">
            <el-icon><Download /></el-icon>
            Export
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="json">Export as JSON</el-dropdown-item>
              <el-dropdown-item command="csv">Export as CSV/Excel</el-dropdown-item>
              <el-dropdown-item command="pdf">Export as PDF</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <div v-loading="loading" class="report-content">
      <!-- Summary Cards -->
      <div class="summary-cards">
        <el-card class="stat-card completed">
          <div class="stat-icon">✅</div>
          <div class="stat-content">
            <div class="stat-value">{{ report?.summary?.completed_tasks || 0 }}</div>
            <div class="stat-label">Completed Tasks</div>
          </div>
        </el-card>

        <el-card class="stat-card in-progress">
          <div class="stat-icon">🔄</div>
          <div class="stat-content">
            <div class="stat-value">{{ report?.summary?.in_progress_tasks || 0 }}</div>
            <div class="stat-label">In Progress</div>
          </div>
        </el-card>

        <el-card class="stat-card pending">
          <div class="stat-icon">⏳</div>
          <div class="stat-content">
            <div class="stat-value">{{ report?.summary?.pending_tasks || 0 }}</div>
            <div class="stat-label">Pending</div>
          </div>
        </el-card>

        <el-card class="stat-card blocked">
          <div class="stat-icon">🚫</div>
          <div class="stat-content">
            <div class="stat-value">{{ report?.summary?.blocked_tasks || 0 }}</div>
            <div class="stat-label">Blocked</div>
          </div>
        </el-card>
      </div>

      <!-- Progress Section -->
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card class="progress-card">
            <template #header>
              <div class="card-header">
                <span>Overall Progress</span>
                <el-tag :type="getProgressType(report?.summary?.completion_rate)">
                  {{ report?.summary?.completion_rate || 0 }}%
                </el-tag>
              </div>
            </template>
            <el-progress 
              :percentage="report?.summary?.completion_rate || 0" 
              :stroke-width="20"
              :color="progressColors"
            />
            <div class="progress-details">
              <div class="detail-item">
                <span>Total Tasks:</span>
                <strong>{{ report?.summary?.total_tasks || 0 }}</strong>
              </div>
              <div class="detail-item">
                <span>Average Progress:</span>
                <strong>{{ report?.summary?.average_progress || 0 }}%</strong>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card class="progress-card">
            <template #header>
              <div class="card-header">
                <span>Milestones</span>
                <el-tag :type="getMilestoneType(report?.milestones?.completion_rate)">
                  {{ report?.milestones?.completed || 0 }} / {{ report?.milestones?.total || 0 }}
                </el-tag>
              </div>
            </template>
            <el-progress 
              :percentage="report?.milestones?.completion_rate || 0" 
              :stroke-width="20"
              :color="progressColors"
            />
            <div class="progress-details">
              <div class="detail-item">
                <span>Completion Rate:</span>
                <strong>{{ report?.milestones?.completion_rate || 0 }}%</strong>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- Timeline Section -->
      <el-card class="timeline-card">
        <template #header>
          <div class="card-header">
            <span>Project Timeline</span>
          </div>
        </template>
        <div class="timeline-info">
          <div class="timeline-item">
            <el-icon class="timeline-icon"><Calendar /></el-icon>
            <div>
              <div class="timeline-label">Start Date</div>
              <div class="timeline-value">{{ formatDate(report?.timeline?.start_date) }}</div>
            </div>
          </div>
          <div class="timeline-item">
            <el-icon class="timeline-icon"><Clock /></el-icon>
            <div>
              <div class="timeline-label">Days Elapsed</div>
              <div class="timeline-value">{{ report?.timeline?.days_elapsed || 0 }} days</div>
            </div>
          </div>
          <div class="timeline-item">
            <el-icon class="timeline-icon"><Timer /></el-icon>
            <div>
              <div class="timeline-label">Days Remaining</div>
              <div class="timeline-value">{{ report?.timeline?.days_remaining || 0 }} days</div>
            </div>
          </div>
          <div class="timeline-item">
            <el-icon class="timeline-icon"><Flag /></el-icon>
            <div>
              <div class="timeline-label">Deadline</div>
              <div class="timeline-value">{{ formatDate(report?.timeline?.deadline) }}</div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- Tasks by Status Chart -->
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>Task Distribution</span>
              </div>
            </template>
            <div class="chart-container">
              <div class="bar-chart">
                <div class="bar-item">
                  <div class="bar-label">Completed</div>
                  <div class="bar-wrapper">
                    <div class="bar completed-bar" :style="{ width: getBarWidth(report?.summary?.completed_tasks, report?.summary?.total_tasks) }">
                      {{ report?.summary?.completed_tasks || 0 }}
                    </div>
                  </div>
                </div>
                <div class="bar-item">
                  <div class="bar-label">In Progress</div>
                  <div class="bar-wrapper">
                    <div class="bar in-progress-bar" :style="{ width: getBarWidth(report?.summary?.in_progress_tasks, report?.summary?.total_tasks) }">
                      {{ report?.summary?.in_progress_tasks || 0 }}
                    </div>
                  </div>
                </div>
                <div class="bar-item">
                  <div class="bar-label">Pending</div>
                  <div class="bar-wrapper">
                    <div class="bar pending-bar" :style="{ width: getBarWidth(report?.summary?.pending_tasks, report?.summary?.total_tasks) }">
                      {{ report?.summary?.pending_tasks || 0 }}
                    </div>
                  </div>
                </div>
                <div class="bar-item">
                  <div class="bar-label">Blocked</div>
                  <div class="bar-wrapper">
                    <div class="bar blocked-bar" :style="{ width: getBarWidth(report?.summary?.blocked_tasks, report?.summary?.total_tasks) }">
                      {{ report?.summary?.blocked_tasks || 0 }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>Team Performance</span>
              </div>
            </template>
            <div class="team-stats">
              <div v-for="member in report?.assignee_stats" :key="member.user_id" class="team-member">
                <div class="member-info">
                  <div class="member-name">{{ member.name }}</div>
                  <div class="member-rate">{{ member.completion_rate }}%</div>
                </div>
                <el-progress 
                  :percentage="member.completion_rate" 
                  :stroke-width="8"
                  :show-text="false"
                />
                <div class="member-details">
                  <span>{{ member.completed }}/{{ member.total }} completed</span>
                  <span>{{ member.in_progress }} in progress</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- Overdue and Upcoming Tasks -->
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>Overdue Tasks</span>
                <el-tag type="danger">{{ report?.overdue_tasks?.length || 0 }}</el-tag>
              </div>
            </template>
            <el-empty v-if="!report?.overdue_tasks || report.overdue_tasks.length === 0" description="No overdue tasks" />
            <div v-else class="task-list">
              <div v-for="task in report.overdue_tasks" :key="task.id" class="task-item overdue">
                <div class="task-info">
                  <div class="task-title">{{ task.title }}</div>
                  <div class="task-meta">
                    <el-tag size="small" :type="getPriorityType(task.priority)">{{ task.priority }}</el-tag>
                    <span class="task-date">Due: {{ formatDate(task.end_date) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>Upcoming Deadlines (Next 7 Days)</span>
                <el-tag type="warning">{{ report?.upcoming_tasks?.length || 0 }}</el-tag>
              </div>
            </template>
            <el-empty v-if="!report?.upcoming_tasks || report.upcoming_tasks.length === 0" description="No upcoming deadlines" />
            <div v-else class="task-list">
              <div v-for="task in report.upcoming_tasks" :key="task.id" class="task-item upcoming">
                <div class="task-info">
                  <div class="task-title">{{ task.title }}</div>
                  <div class="task-meta">
                    <el-tag size="small" :type="getPriorityType(task.priority)">{{ task.priority }}</el-tag>
                    <span class="task-date">Due: {{ formatDate(task.end_date) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- Critical Path -->
      <el-card>
        <template #header>
          <div class="card-header">
            <span>🎯 Critical Path (Tasks Affecting Project Completion)</span>
            <el-tag type="danger">{{ report?.critical_path?.length || 0 }} tasks</el-tag>
          </div>
        </template>
        <el-empty v-if="!report?.critical_path || report.critical_path.length === 0" description="No critical path identified" />
        <div v-else class="task-list">
          <div v-for="(task, index) in report.critical_path" :key="task.id" class="task-item critical">
            <div class="critical-badge">{{ index + 1 }}</div>
            <div class="task-info">
              <div class="task-title">{{ task.title }}</div>
              <div class="task-meta">
                <el-tag size="small" :type="getPriorityType(task.priority)">{{ task.priority }}</el-tag>
                <el-tag size="small" :type="task.status === 'completed' ? 'success' : 'warning'">{{ task.status }}</el-tag>
                <span class="task-date">{{ formatDate(task.start_date) }} → {{ formatDate(task.end_date) }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- Recently Completed Tasks -->
      <el-card>
        <template #header>
          <div class="card-header">
            <span>Recently Completed (Last 7 Days)</span>
            <el-tag type="success">{{ report?.recent_completed?.length || 0 }}</el-tag>
          </div>
        </template>
        <el-empty v-if="!report?.recent_completed || report.recent_completed.length === 0" description="No recently completed tasks" />
        <div v-else class="task-list horizontal">
          <div v-for="task in report.recent_completed" :key="task.id" class="task-item completed">
            <div class="task-info">
              <div class="task-title">{{ task.title }}</div>
              <div class="task-meta">
                <el-tag size="small" type="success">completed</el-tag>
                <span class="task-assignee">{{ task.assigned_to_name || 'Unassigned' }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Refresh, Download, Calendar, Clock, Timer, Flag } from '@element-plus/icons-vue'
import api from '@/services/api'

const route = useRoute()
const loading = ref(false)
const project = ref(null)
const report = ref(null)

const progressColors = [
  { color: '#f56c6c', percentage: 30 },
  { color: '#e6a23c', percentage: 60 },
  { color: '#67c23a', percentage: 100 }
]

const fetchReport = async () => {
  loading.value = true
  try {
    const response = await api.get(`/projects/${route.params.id}/progress-report`)
    report.value = response.data
    project.value = response.data.project
  } catch (error) {
    console.error('Failed to fetch report:', error)
    ElMessage.error('Failed to load progress report')
  } finally {
    loading.value = false
  }
}

const handleExport = async (format) => {
  try {
    if (format === 'json') {
      const response = await api.get(`/export/projects/${route.params.id}/json`)
      const dataStr = JSON.stringify(response.data, null, 2)
      const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
      const exportFileDefaultName = `project_${route.params.id}_export.json`
      
      const linkElement = document.createElement('a')
      linkElement.setAttribute('href', dataUri)
      linkElement.setAttribute('download', exportFileDefaultName)
      linkElement.click()
      
      ElMessage.success('Report exported as JSON')
    } else if (format === 'csv') {
      const response = await api.get(`/export/projects/${route.params.id}/csv`, {
        responseType: 'text'
      })
      const blob = new Blob([response.data], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `project_${route.params.id}_tasks.csv`
      link.click()
      window.URL.revokeObjectURL(url)
      
      ElMessage.success('Report exported as CSV')
    } else if (format === 'pdf') {
      // For PDF, we'll use the browser's print functionality
      ElMessage.info('Opening print dialog for PDF export...')
      setTimeout(() => {
        window.print()
      }, 500)
    }
  } catch (error) {
    console.error('Export failed:', error)
    ElMessage.error('Failed to export report')
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const getProgressType = (rate) => {
  if (rate >= 80) return 'success'
  if (rate >= 50) return 'warning'
  return 'danger'
}

const getMilestoneType = (rate) => {
  if (rate >= 70) return 'success'
  if (rate >= 40) return 'warning'
  return 'danger'
}

const getPriorityType = (priority) => {
  const types = {
    critical: 'danger',
    high: 'warning',
    medium: '',
    low: 'info'
  }
  return types[priority] || ''
}

const getBarWidth = (value, total) => {
  if (!total || total === 0) return '0%'
  return `${(value / total * 100)}%`
}

onMounted(() => {
  fetchReport()
})
</script>

<style scoped>
.project-report {
  padding: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.report-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
}

.page-title {
  flex: 1;
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color:rgb(30, 160, 50);
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  letter-spacing: 0.5px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.report-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  font-size: 48px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.stat-card.completed .stat-value {
  color: #67c23a;
}

.stat-card.in-progress .stat-value {
  color: #409eff;
}

.stat-card.pending .stat-value {
  color: #e6a23c;
}

.stat-card.blocked .stat-value {
  color: #f56c6c;
}

.progress-card {
  margin-bottom: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.progress-details {
  margin-top: 16px;
  display: flex;
  justify-content: space-between;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-item span {
  font-size: 13px;
  color: #909399;
}

.detail-item strong {
  font-size: 20px;
  color: #303133;
}

.timeline-card {
  margin: 0;
}

.timeline-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
}

.timeline-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.timeline-icon {
  font-size: 32px;
  color: #409eff;
}

.timeline-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 4px;
}

.timeline-value {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.chart-container {
  padding: 12px 0;
}

.bar-chart {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.bar-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.bar-label {
  width: 100px;
  font-size: 13px;
  color: #606266;
}

.bar-wrapper {
  flex: 1;
  background: #f5f7fa;
  border-radius: 4px;
  overflow: hidden;
}

.bar {
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 8px;
  color: #fff;
  font-weight: 600;
  font-size: 12px;
  transition: width 0.5s ease;
  min-width: 30px;
}

.completed-bar {
  background: linear-gradient(90deg, #67c23a, #85ce61);
}

.in-progress-bar {
  background: linear-gradient(90deg, #409eff, #66b1ff);
}

.pending-bar {
  background: linear-gradient(90deg, #e6a23c, #f0c36d);
}

.blocked-bar {
  background: linear-gradient(90deg, #f56c6c, #f78989);
}

.team-stats {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.team-member {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.member-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.member-name {
  font-weight: 600;
  color: #303133;
}

.member-rate {
  font-size: 14px;
  font-weight: 600;
  color: #409eff;
}

.member-details {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #909399;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 300px;
  overflow-y: auto;
}

.task-list.horizontal {
  flex-direction: row;
  flex-wrap: wrap;
}

.task-item {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  border-left: 4px solid;
  transition: all 0.2s;
}

.task-item:hover {
  background: #ebeef5;
  transform: translateX(4px);
}

.task-item.overdue {
  border-left-color: #f56c6c;
}

.task-item.upcoming {
  border-left-color: #e6a23c;
}

.task-item.completed {
  border-left-color: #67c23a;
}

.task-item.critical {
  border-left-color: #f56c6c;
  background: linear-gradient(90deg, #fff5f5, #f5f7fa);
  position: relative;
  padding-left: 56px;
}

.critical-badge {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f56c6c, #f78989);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(245, 108, 108, 0.3);
}

.task-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-title {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: #909399;
}

.task-date, .task-assignee {
  font-size: 12px;
}
</style>

