<template>
  <main-layout>
    <div class="container">
      <div class="page-header">
        <h2 class="page-title">Projects</h2>
        <div style="display: flex; gap: 12px; align-items: center;">
          <el-select
            v-model="selectedProjectToDelete"
            placeholder="Select project to delete"
            style="width: 220px"
            clearable
          >
            <el-option
              v-for="project in projectStore.projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
          <el-button
            type="danger"
            @click="handleDeleteProject"
            :disabled="!selectedProjectToDelete"
          >
            <el-icon><Delete /></el-icon>
            Delete Project
          </el-button>
          <el-divider direction="vertical" />
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            Create Project
          </el-button>
        </div>
      </div>

      <el-row :gutter="20">
        <el-col
          v-for="project in projectStore.projects"
          :key="project.id"
          :span="8"
        >
          <el-card class="project-card" @click="goToProject(project.id)">
            <div class="project-header" :style="{ borderLeftColor: project.color }">
              <h3>{{ project.name }}</h3>
              <el-tag :type="getStatusType(project.status)">{{ project.status }}</el-tag>
            </div>
            
            <p class="project-description">{{ project.description || 'No description' }}</p>
            
            <div class="project-stats">
              <span><el-icon><List /></el-icon> {{ project.tasks_count }} tasks</span>
              <span><el-icon><User /></el-icon> {{ project.members_count }} members</span>
            </div>
            
            <el-progress
              :percentage="getCompletionRate(project)"
              :color="project.color"
            />
          </el-card>
        </el-col>
      </el-row>

      <!-- Admin Tasks Management Section -->
      <el-divider content-position="left">
        <span style="font-size: 16px; font-weight: 600;">Tasks Management (Admin)</span>
      </el-divider>

      <el-card class="tasks-card">
        <template #header>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span>All Tasks</span>
            <el-select v-model="taskFilter" placeholder="Filter by project" style="width: 200px" clearable>
              <el-option label="All Projects" value="" />
              <el-option
                v-for="project in projectStore.projects"
                :key="project.id"
                :label="project.name"
                :value="project.id"
              />
            </el-select>
          </div>
        </template>

        <el-table :data="filteredTasks" style="width: 100%" v-loading="loadingTasks">
          <el-table-column prop="title" label="Task" min-width="200" />
          
          <el-table-column prop="project_id" label="Project" width="150">
            <template #default="scope">
              <span>{{ getProjectName(scope.row.project_id) }}</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="status" label="Status" width="120">
            <template #default="scope">
              <el-tag :type="getTaskStatusType(scope.row.status)" size="small">
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
          
          <el-table-column prop="assigned_to_name" label="Assigned To" width="150">
            <template #default="scope">
              <span>{{ scope.row.assigned_to_name || 'Unassigned' }}</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="end_date" label="Due Date" width="120">
            <template #default="scope">
              {{ formatDate(scope.row.end_date) }}
            </template>
          </el-table-column>
          
          <el-table-column label="Actions" width="100" fixed="right">
            <template #default="scope">
              <el-button
                type="danger"
                size="small"
                text
                @click="handleDeleteTask(scope.row)"
              >
                <el-icon><Delete /></el-icon>
                Delete
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-empty v-if="!loadingTasks && filteredTasks.length === 0" description="No tasks found" />
      </el-card>

      <!-- Create Project Dialog -->
      <el-dialog v-model="showCreateDialog" title="Create New Project" width="500px">
        <el-form :model="newProject" label-position="top">
          <el-form-item label="Project Name">
            <el-input v-model="newProject.name" placeholder="Enter project name" />
          </el-form-item>
          
          <el-form-item label="Description">
            <el-input
              v-model="newProject.description"
              type="textarea"
              :rows="3"
              placeholder="Enter project description"
            />
          </el-form-item>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Start Date">
                <el-date-picker
                  v-model="newProject.start_date"
                  type="date"
                  placeholder="Select date"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            
            <el-col :span="12">
              <el-form-item label="Deadline">
                <el-date-picker
                  v-model="newProject.deadline"
                  type="date"
                  placeholder="Select date"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item label="Color">
            <el-color-picker v-model="newProject.color" />
          </el-form-item>
          
          <el-form-item label="Team Members">
            <el-select
              v-model="selectedMembers"
              multiple
              filterable
              placeholder="Select team members"
              style="width: 100%"
              :loading="loadingUsers"
            >
              <el-option
                v-for="user in availableUsers"
                :key="user.id"
                :label="user.full_name || user.username"
                :value="user.id"
              >
                <div style="display: flex; align-items: center; gap: 8px;">
                  <el-avatar :size="24" :src="user.avatar" />
                  <span>{{ user.full_name || user.username }}</span>
                  <el-tag v-if="user.role" size="small" type="info">{{ user.role }}</el-tag>
                </div>
              </el-option>
            </el-select>
          </el-form-item>
        </el-form>
        
        <template #footer>
          <el-button @click="showCreateDialog = false">Cancel</el-button>
          <el-button type="primary" @click="handleCreate">Create</el-button>
        </template>
      </el-dialog>
    </div>
  </main-layout>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectStore } from '@/stores/projects'
import MainLayout from '@/components/Layout/MainLayout.vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, List, User, Delete } from '@element-plus/icons-vue'
import authAPI from '@/services/api/auth'
import projectAPI from '@/services/api/projects'
import taskAPI from '@/services/api/tasks'

const router = useRouter()
const projectStore = useProjectStore()
const showCreateDialog = ref(false)
const users = ref([])
const selectedMembers = ref([])
const loadingUsers = ref(false)
const selectedProjectToDelete = ref(null)

const newProject = reactive({
  name: '',
  description: '',
  start_date: null,
  deadline: null,
  color: '#409eff'
})

// Tasks management
const tasks = ref([])
const loadingTasks = ref(false)
const taskFilter = ref('')

const filteredTasks = computed(() => {
  if (!taskFilter.value) return tasks.value
  return tasks.value.filter(task => task.project_id === taskFilter.value)
})

// Get current user from localStorage or auth store
const currentUser = computed(() => {
  const userStr = localStorage.getItem('user')
  return userStr ? JSON.parse(userStr) : null
})

// Filter out current user from available users
const availableUsers = computed(() => {
  if (!currentUser.value) return users.value
  return users.value.filter(user => user.id !== currentUser.value.id)
})

// Fetch users when dialog opens
const fetchUsers = async () => {
  loadingUsers.value = true
  try {
    const response = await authAPI.getUsers()
    users.value = response.data.users || []
  } catch (error) {
    console.error('Failed to fetch users:', error)
    ElMessage.error('Failed to load users')
  } finally {
    loadingUsers.value = false
  }
}

// Watch dialog visibility to fetch users
watch(showCreateDialog, (isOpen) => {
  if (isOpen) {
    fetchUsers()
    selectedMembers.value = []
  }
})

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

const getCompletionRate = (project) => {
  if (!project.tasks_count) return 0
  return Math.round((project.completed_tasks / project.tasks_count) * 100)
}

const goToProject = (id) => {
  router.push(`/projects/${id}`)
}

const handleCreate = async () => {
  if (!newProject.name) {
    ElMessage.warning('Please enter project name')
    return
  }

  const projectData = {
    name: newProject.name,
    description: newProject.description,
    start_date: newProject.start_date?.toISOString(),
    deadline: newProject.deadline?.toISOString(),
    color: newProject.color
  }

  const result = await projectStore.createProject(projectData)

  if (result.success) {
    // Add selected members to the project
    if (selectedMembers.value.length > 0) {
      try {
        for (const userId of selectedMembers.value) {
          await projectAPI.addMember(result.project.id, {
            user_id: userId,
            role: 'member'
          })
        }
        ElMessage.success(`Project created with ${selectedMembers.value.length} members`)
      } catch (error) {
        console.error('Failed to add members:', error)
        ElMessage.warning('Project created but some members could not be added')
      }
    } else {
      ElMessage.success('Project created successfully')
    }

    showCreateDialog.value = false
    Object.assign(newProject, {
      name: '',
      description: '',
      start_date: null,
      deadline: null,
      color: '#409eff'
    })
    selectedMembers.value = []
  } else {
    ElMessage.error(result.error)
  }
}

// Tasks management functions
const fetchTasks = async () => {
  loadingTasks.value = true
  try {
    const response = await taskAPI.getAll()
    tasks.value = response.data.tasks || []
  } catch (error) {
    console.error('Failed to fetch tasks:', error)
    ElMessage.error('Failed to load tasks')
  } finally {
    loadingTasks.value = false
  }
}

const getProjectName = (projectId) => {
  const project = projectStore.projects.find(p => p.id === projectId)
  return project?.name || `Project #${projectId}`
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString()
}

const getTaskStatusType = (status) => {
  const types = {
    pending: 'info',
    in_progress: 'warning',
    completed: 'success',
    blocked: 'danger',
    cancelled: 'info'
  }
  return types[status] || ''
}

const handleDeleteTask = async (task) => {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete task "${task.title}"?`,
      'Delete Task',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
    )

    await taskAPI.delete(task.id)
    ElMessage.success('Task deleted successfully')
    fetchTasks()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete task:', error)
      ElMessage.error(error.response?.data?.error || 'Failed to delete task')
    }
  }
}

const handleDeleteProject = async () => {
  if (!selectedProjectToDelete.value) {
    ElMessage.warning('Please select a project to delete')
    return
  }

  const project = projectStore.projects.find(p => p.id === selectedProjectToDelete.value)
  if (!project) {
    ElMessage.error('Project not found')
    return
  }

  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete project "${project.name}"? This action cannot be undone and all associated tasks will be removed.`,
      'Delete Project',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
    )

    const result = await projectStore.deleteProject(selectedProjectToDelete.value)
    if (result.success) {
      ElMessage.success(`Project "${project.name}" deleted successfully`)
      selectedProjectToDelete.value = null
      fetchTasks()
    } else {
      ElMessage.error(result.error || 'Failed to delete project')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete project:', error)
      ElMessage.error(error.response?.data?.error || 'Failed to delete project')
    }
  }
}

onMounted(() => {
  projectStore.fetchProjects()
  fetchTasks()
})
</script>

<style scoped>
.project-card {
  margin-bottom: 24px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 20px;
  overflow: hidden;
  position: relative;
  background: white;
  border: none;
}

.project-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 6px;
  background: linear-gradient(90deg, 
    var(--project-color, #409eff) 0%,
    var(--project-color-light, #79bbff) 100%
  );
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.4s ease;
}

.project-card:hover::before {
  transform: scaleX(1);
}

.project-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 20px 16px 20px;
  margin-bottom: 12px;
  position: relative;
}

.project-header::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(180deg,
    var(--project-color, #409eff) 0%,
    var(--project-color-light, #79bbff) 100%
  );
  border-radius: 0 4px 4px 0;
}

.project-header h3 {
  margin: 0 0 0 16px;
  font-size: 20px;
  font-weight: 700;
  color: #303133;
  letter-spacing: -0.3px;
}

.project-description {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  margin: 0 20px 20px 20px;
  min-height: 48px;
  max-height: 48px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.project-stats {
  display: flex;
  gap: 24px;
  margin: 0 20px 16px 20px;
  padding: 12px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
  border-radius: 12px;
}

.project-stats span {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #606266;
  font-size: 13px;
  font-weight: 600;
}

.project-stats span .el-icon {
  color: var(--project-color, #409eff);
}

:deep(.el-progress) {
  margin: 0 20px 20px 20px;
}

:deep(.el-progress__text) {
  font-weight: 700;
}

.tasks-card {
  margin-top: 20px;
}

.priority-low {
  color: #67c23a;
}

.priority-medium {
  color: #e6a23c;
}

.priority-high {
  color: #f56c6c;
}

.priority-critical {
  color: #ff0000;
  font-weight: bold;
}
</style>
