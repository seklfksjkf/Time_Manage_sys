<template>
  <main-layout>
    <div class="container">
      <div class="page-header">
        <h2 class="page-title">Projects</h2>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          Create Project
        </el-button>
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
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectStore } from '@/stores/projects'
import MainLayout from '@/components/Layout/MainLayout.vue'
import { ElMessage } from 'element-plus'
import { Plus, List, User } from '@element-plus/icons-vue'

const router = useRouter()
const projectStore = useProjectStore()
const showCreateDialog = ref(false)

const newProject = reactive({
  name: '',
  description: '',
  start_date: null,
  deadline: null,
  color: '#409eff'
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
    ElMessage.success('Project created successfully')
    showCreateDialog.value = false
    Object.assign(newProject, {
      name: '',
      description: '',
      start_date: null,
      deadline: null,
      color: '#409eff'
    })
  } else {
    ElMessage.error(result.error)
  }
}

onMounted(() => {
  projectStore.fetchProjects()
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
</style>
