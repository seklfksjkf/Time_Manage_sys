<template>
  <main-layout>
    <div class="container" v-if="project">
      <div class="page-header">
        <div>
          <el-button @click="$router.back()" text>
            <el-icon><ArrowLeft /></el-icon>
            Back
          </el-button>
          <h2 class="page-title">{{ project.name }}</h2>
        </div>
        <div>
          <el-button @click="goToTimeline">
            <el-icon><Calendar /></el-icon>
            View Timeline
          </el-button>
          <el-button @click="goToReport">
            <el-icon><Document /></el-icon>
            View Report
          </el-button>
          <el-button type="primary" @click="showTaskDialog = true">
            <el-icon><Plus /></el-icon>
            Add Task
          </el-button>
        </div>
      </div>

      <el-row :gutter="20">
        <el-col :span="18">
          <el-card class="info-card">
            <el-descriptions :column="2">
              <el-descriptions-item label="Status">
                <el-tag :type="getStatusType(project.status)">{{ project.status }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="Owner">{{ project.owner_name }}</el-descriptions-item>
              <el-descriptions-item label="Start Date">{{ formatDate(project.start_date) }}</el-descriptions-item>
              <el-descriptions-item label="Deadline">{{ formatDate(project.deadline) }}</el-descriptions-item>
              <el-descriptions-item label="Description" :span="2">
                {{ project.description || 'No description' }}
              </el-descriptions-item>
            </el-descriptions>
          </el-card>

          <el-card class="tasks-card">
            <template #header>
              <span>Tasks ({{ tasks.length }})</span>
            </template>
            
            <el-table :data="tasks" style="width: 100%">
              <el-table-column prop="title" label="Task" />
              <el-table-column prop="status" label="Status" width="120">
                <template #default="scope">
                  <el-tag :class="`status-${scope.row.status}`" size="small">
                    {{ scope.row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="priority" label="Priority" width="100">
                <template #default="scope">
                  <span :class="`priority-${scope.row.priority}`">
                    {{ scope.row.priority }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="assigned_to_name" label="Assigned To" width="150" />
              <el-table-column prop="progress" label="Progress" width="120">
                <template #default="scope">
                  <el-progress :percentage="scope.row.progress" :stroke-width="6" />
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card class="members-card">
            <template #header>
              <span>Team Members</span>
            </template>
            <div class="member-list">
              <div v-for="member in members" :key="member.id" class="member-item">
                <el-avatar :size="32">{{ getInitials(member.user_name) }}</el-avatar>
                <span>{{ member.user_name }}</span>
                <el-tag size="small">{{ member.role }}</el-tag>
              </div>
            </div>
          </el-card>

          <el-card class="history-card" style="margin-top: 20px;">
            <template #header>
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>Version History</span>
                <el-button size="small" @click="loadVersionHistory" :loading="historyLoading">
                  <el-icon><Refresh /></el-icon>
                </el-button>
              </div>
            </template>
            <el-timeline v-if="versionHistory.length > 0">
              <el-timeline-item
                v-for="item in versionHistory.slice(0, 10)"
                :key="item.id"
                :timestamp="formatDateTime(item.changed_at)"
                placement="top"
              >
                <div class="history-item">
                  <div class="history-type">{{ item.change_type }}</div>
                  <div class="history-details">{{ item.changes || 'No details' }}</div>
                  <div class="history-user">by {{ item.changed_by_name || 'Unknown' }}</div>
                </div>
              </el-timeline-item>
            </el-timeline>
            <el-empty v-else description="No version history" :image-size="80" />
          </el-card>
        </el-col>
      </el-row>

      <!-- Add Task Dialog -->
      <el-dialog v-model="showTaskDialog" title="Add New Task" width="600px">
        <el-form :model="newTask" label-position="top">
          <el-form-item label="Task Title">
            <el-input v-model="newTask.title" placeholder="Enter task title" />
          </el-form-item>
          
          <el-form-item label="Description">
            <el-input
              v-model="newTask.description"
              type="textarea"
              :rows="3"
              placeholder="Enter task description"
            />
          </el-form-item>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Start Date">
                <el-date-picker
                  v-model="newTask.start_date"
                  type="date"
                  placeholder="Select date"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            
            <el-col :span="12">
              <el-form-item label="End Date">
                <el-date-picker
                  v-model="newTask.end_date"
                  type="date"
                  placeholder="Select date"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Priority">
                <el-select v-model="newTask.priority" style="width: 100%">
                  <el-option label="Low" value="low" />
                  <el-option label="Medium" value="medium" />
                  <el-option label="High" value="high" />
                  <el-option label="Critical" value="critical" />
                </el-select>
              </el-form-item>
            </el-col>
            
            <el-col :span="12">
              <el-form-item label="Assign To">
                <el-select v-model="newTask.assigned_to" style="width: 100%">
                  <el-option
                    v-for="member in members"
                    :key="member.user_id"
                    :label="member.user_name"
                    :value="member.user_id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
        
        <template #footer>
          <el-button @click="showTaskDialog = false">Cancel</el-button>
          <el-button type="primary" @click="handleCreateTask">Create</el-button>
        </template>
      </el-dialog>
    </div>
  </main-layout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MainLayout from '@/components/Layout/MainLayout.vue'
import projectAPI from '@/services/api/projects'
import taskAPI from '@/services/api/tasks'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Calendar, Plus, Document } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const project = ref(null)
const tasks = ref([])
const members = ref([])
const versionHistory = ref([])
const historyLoading = ref(false)
const showTaskDialog = ref(false)

const newTask = reactive({
  title: '',
  description: '',
  start_date: null,
  end_date: null,
  priority: 'medium',
  assigned_to: null
})

const fetchProject = async () => {
  try {
    const response = await projectAPI.getById(route.params.id)
    project.value = response.data.project
  } catch (error) {
    ElMessage.error('Failed to load project')
  }
}

const fetchTasks = async () => {
  try {
    const response = await taskAPI.getAll({ project_id: route.params.id })
    tasks.value = response.data.tasks
  } catch (error) {
    console.error('Failed to load tasks:', error)
  }
}

const fetchMembers = async () => {
  try {
    const response = await projectAPI.getMembers(route.params.id)
    members.value = response.data.members
  } catch (error) {
    console.error('Failed to load members:', error)
  }
}

const getStatusType = (status) => {
  const types = {
    planning: 'info',
    in_progress: '',
    completed: 'success',
    on_hold: 'warning',
    cancelled: 'danger'
  }
  return types[status] || ''
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString()
}

const formatDateTime = (dateTime) => {
  if (!dateTime) return 'N/A'
  const date = new Date(dateTime)
  return date.toLocaleString('en-US', { 
    month: 'short', 
    day: 'numeric', 
    year: 'numeric',
    hour: '2-digit', 
    minute: '2-digit'
  })
}

const loadVersionHistory = async () => {
  historyLoading.value = true
  try {
    const response = await projectAPI.getVersionHistory(route.params.id)
    versionHistory.value = response.data.history || []
  } catch (error) {
    console.error('Failed to load version history:', error)
    ElMessage.warning('Failed to load version history')
  } finally {
    historyLoading.value = false
  }
}

const getInitials = (name) => {
  return name?.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) || 'U'
}

const goToTimeline = () => {
  router.push(`/projects/${route.params.id}/timeline`)
}

const goToReport = () => {
  router.push(`/projects/${route.params.id}/report`)
}

const handleCreateTask = async () => {
  if (!newTask.title || !newTask.start_date || !newTask.end_date) {
    ElMessage.warning('Please fill in required fields')
    return
  }

  const taskData = {
    project_id: Number(route.params.id),
    title: newTask.title,
    description: newTask.description,
    start_date: newTask.start_date.toISOString(),
    end_date: newTask.end_date.toISOString(),
    priority: newTask.priority,
    assigned_to: newTask.assigned_to
  }

  try {
    await taskAPI.create(taskData)
    ElMessage.success('Task created successfully')
    showTaskDialog.value = false
    fetchTasks()
    Object.assign(newTask, {
      title: '',
      description: '',
      start_date: null,
      end_date: null,
      priority: 'medium',
      assigned_to: null
    })
  } catch (error) {
    ElMessage.error('Failed to create task')
  }
}

onMounted(() => {
  fetchProject()
  fetchTasks()
  fetchMembers()
  loadVersionHistory()
})
</script>

<style scoped>
.info-card,
.tasks-card,
.members-card,
.history-card {
  margin-bottom: 20px;
}

.history-item {
  font-size: 13px;
}

.history-type {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
  text-transform: capitalize;
}

.history-details {
  color: #606266;
  margin-bottom: 4px;
  font-size: 12px;
}

.history-user {
  color: #909399;
  font-size: 11px;
  font-style: italic;
}

.member-list {
  max-height: 400px;
  overflow-y: auto;
}

.member-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #e4e7ed;
}

.member-item:last-child {
  border-bottom: none;
}

.member-item span {
  flex: 1;
  font-size: 14px;
}
</style>

