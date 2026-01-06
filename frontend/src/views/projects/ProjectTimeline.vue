<template>
  <div class="gantt-fullscreen">
    <div class="container">
      <div class="page-header">
        <div>
          <el-button @click="$router.back()" text>
            <el-icon><ArrowLeft /></el-icon>
            Back
          </el-button>
          <h2 class="page-title">{{ project?.name }} - Gantt Chart</h2>
        </div>
        <div class="header-actions">
          <el-button-group>
            <el-button 
              :type="zoomLevel === 'day' ? 'primary' : ''" 
              @click="zoomLevel = 'day'"
            >
              Daily View
            </el-button>
            <el-button 
              :type="zoomLevel === 'week' ? 'primary' : ''" 
              @click="zoomLevel = 'week'"
            >
              Weekly View
            </el-button>
            <el-button 
              :type="zoomLevel === 'month' ? 'primary' : ''" 
              @click="zoomLevel = 'month'"
            >
              Monthly View
            </el-button>
          </el-button-group>
          <el-button type="primary" @click="showAddTaskDialog">
            <el-icon><Plus /></el-icon>
            Add Task
          </el-button>
          <el-button @click="fetchTimeline" :loading="loading">
            <el-icon><Refresh /></el-icon>
            Refresh
          </el-button>
        </div>
      </div>

      <el-card v-loading="loading">
        <gantt-chart
          v-if="tasks.length > 0"
          :tasks="tasks"
          :milestones="milestones"
          :start-date="projectStartDate"
          :end-date="projectEndDate"
          :zoom-level="zoomLevel"
          @task-click="handleTaskClick"
          @task-edit="handleEditTask"
          @task-delete="handleDeleteTask"
          @task-update="handleTaskUpdate"
        />
        <el-empty v-else description="No tasks in this project. Please add some tasks first." />
      </el-card>

      <!-- Task Edit/Add Dialog -->
      <el-dialog 
        v-model="showTaskDialog" 
        :title="isEditMode ? 'Edit Task' : 'Add Task'" 
        width="600px"
        @close="resetTaskForm"
      >
        <el-form :model="taskForm" label-width="120px" ref="taskFormRef">
          <el-form-item label="Title" required>
            <el-input v-model="taskForm.title" placeholder="Enter task title" />
          </el-form-item>
          
          <el-form-item label="Description">
            <el-input 
              v-model="taskForm.description" 
              type="textarea" 
              :rows="3"
              placeholder="Enter task description"
            />
          </el-form-item>
          
          <el-form-item label="Status" required>
            <el-select v-model="taskForm.status" placeholder="Select status">
              <el-option label="Pending" value="pending" />
              <el-option label="In Progress" value="in_progress" />
              <el-option label="Completed" value="completed" />
              <el-option label="Blocked" value="blocked" />
              <el-option label="Cancelled" value="cancelled" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="Priority" required>
            <el-select v-model="taskForm.priority" placeholder="Select priority">
              <el-option label="Low" value="low" />
              <el-option label="Medium" value="medium" />
              <el-option label="High" value="high" />
              <el-option label="Critical" value="critical" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="Start Date" required>
            <el-date-picker
              v-model="taskForm.start_date"
              type="date"
              placeholder="Select start date"
              style="width: 100%"
            />
          </el-form-item>
          
          <el-form-item label="End Date" required>
            <el-date-picker
              v-model="taskForm.end_date"
              type="date"
              placeholder="Select end date"
              style="width: 100%"
            />
          </el-form-item>
          
          <el-form-item label="Progress">
            <el-slider v-model="taskForm.progress" :step="5" show-stops />
          </el-form-item>
        </el-form>
        
        <template #footer>
          <el-button @click="showTaskDialog = false">Cancel</el-button>
          <el-button type="primary" @click="saveTask" :loading="saving">
            {{ isEditMode ? 'Update' : 'Create' }}
          </el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import GanttChart from '@/components/GanttChart.vue'
import projectAPI from '@/services/api/projects'
import timelineAPI from '@/services/api/timeline'
import taskAPI from '@/services/api/tasks'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Refresh, Plus } from '@element-plus/icons-vue'

const route = useRoute()
const project = ref(null)
const tasks = ref([])
const milestones = ref([])
const loading = ref(false)
const saving = ref(false)
const showTaskDialog = ref(false)
const showTaskDetails = ref(false)
const selectedTask = ref(null)
const isEditMode = ref(false)
const taskFormRef = ref(null)
const zoomLevel = ref('day') // 'day', 'week', 'month'

// Convert string dates to Date objects for GanttChart
const projectStartDate = computed(() => {
  if (!project.value?.start_date) return null
  return new Date(project.value.start_date)
})

const projectEndDate = computed(() => {
  if (!project.value?.deadline) return null
  return new Date(project.value.deadline)
})

const taskForm = ref({
  title: '',
  description: '',
  status: 'pending',
  priority: 'medium',
  start_date: null,
  end_date: null,
  progress: 0
})

const fetchTimeline = async () => {
  console.log('🔄 [ProjectTimeline] fetchTimeline called')
  console.log('📍 [ProjectTimeline] Project ID:', route.params.id)
  
  loading.value = true
  try {
    console.log('📡 [ProjectTimeline] Fetching project and timeline...')
    
    const [projectRes, timelineRes] = await Promise.all([
      projectAPI.getById(route.params.id),
      timelineAPI.getProjectTimeline(route.params.id)
    ])
    
    console.log('✅ [ProjectTimeline] Project response:', projectRes.data)
    console.log('✅ [ProjectTimeline] Timeline response:', timelineRes.data)
    
    project.value = projectRes.data.project
    tasks.value = timelineRes.data.tasks || []
    milestones.value = timelineRes.data.milestones || []
    
    console.log('📊 [ProjectTimeline] Tasks count:', tasks.value.length)
    console.log('🏁 [ProjectTimeline] Milestones count:', milestones.value.length)
    
    if (tasks.value.length === 0) {
      ElMessage.warning('No tasks found. Please add tasks to see the Gantt chart.')
    } else {
      console.log('✅ [ProjectTimeline] First task:', tasks.value[0])
    }
  } catch (error) {
    console.error('❌ [ProjectTimeline] Failed to load timeline:', error)
    console.error('❌ [ProjectTimeline] Error details:', error.response?.data || error.message)
    ElMessage.error('Failed to load timeline data')
  } finally {
    loading.value = false
  }
}

const handleTaskClick = (task) => {
  selectedTask.value = task
  showTaskDetails.value = true
}

const showAddTaskDialog = () => {
  isEditMode.value = false
  resetTaskForm()
  showTaskDialog.value = true
}

const handleEditTask = (task) => {
  isEditMode.value = true
  selectedTask.value = task
  taskForm.value = {
    title: task.title,
    description: task.description || '',
    status: task.status,
    priority: task.priority,
    start_date: task.start_date ? new Date(task.start_date) : null,
    end_date: task.end_date ? new Date(task.end_date) : null,
    progress: task.progress || 0
  }
  showTaskDialog.value = true
}

const handleDeleteTask = async (task) => {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete task "${task.title}"?`,
      'Delete Task',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    await taskAPI.delete(task.id)
    ElMessage.success('Task deleted successfully')
    await fetchTimeline()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete task:', error)
      ElMessage.error('Failed to delete task')
    }
  }
}

const saveTask = async () => {
  if (!taskForm.value.title) {
    ElMessage.warning('Please enter task title')
    return
  }
  
  if (!taskForm.value.start_date || !taskForm.value.end_date) {
    ElMessage.warning('Please select start and end dates')
    return
  }
  
  saving.value = true
  try {
    const taskData = {
      project_id: route.params.id,
      title: taskForm.value.title,
      description: taskForm.value.description,
      status: taskForm.value.status,
      priority: taskForm.value.priority,
      start_date: taskForm.value.start_date.toISOString(),
      end_date: taskForm.value.end_date.toISOString(),
      progress: taskForm.value.progress
    }
    
    if (isEditMode.value) {
      await taskAPI.update(selectedTask.value.id, taskData)
      ElMessage.success('Task updated successfully')
    } else {
      await taskAPI.create(taskData)
      ElMessage.success('Task created successfully')
    }
    
    showTaskDialog.value = false
    await fetchTimeline()
  } catch (error) {
    console.error('Failed to save task:', error)
    ElMessage.error(`Failed to ${isEditMode.value ? 'update' : 'create'} task`)
  } finally {
    saving.value = false
  }
}

const resetTaskForm = () => {
  taskForm.value = {
    title: '',
    description: '',
    status: 'pending',
    priority: 'medium',
    start_date: null,
    end_date: null,
    progress: 0
  }
  selectedTask.value = null
}

const handleTaskUpdate = async (updateData) => {
  try {
    await taskAPI.update(updateData.id, {
      start_date: updateData.start_date,
      end_date: updateData.end_date
    })
    await fetchTimeline()
  } catch (error) {
    console.error('Failed to update task:', error)
    ElMessage.error('Failed to update task dates')
  }
}

const getBarStyle = (task) => {
  const start = new Date(task.start)
  const end = new Date(task.end)
  const projectStart = new Date(project.value?.start_date || start)
  
  const startOffset = Math.max(0, (start - projectStart) / (1000 * 60 * 60 * 24))
  const duration = (end - start) / (1000 * 60 * 60 * 24)
  
  return {
    left: `${startOffset * 30}px`,
    width: `${duration * 30}px`,
    backgroundColor: task.color || '#409eff'
  }
}

const getMilestoneStyle = (milestone) => {
  const date = new Date(milestone.date)
  const projectStart = new Date(project.value?.start_date || date)
  const offset = (date - projectStart) / (1000 * 60 * 60 * 24)
  
  return {
    left: `${offset * 30}px`,
    color: milestone.color || '#e74c3c'
  }
}

const showCriticalPath = async () => {
  try {
    const response = await timelineAPI.getCriticalPath(route.params.id)
    ElMessage.info(`Critical path has ${response.data.critical_path.length} tasks`)
  } catch (error) {
    ElMessage.error('Failed to load critical path')
  }
}

onMounted(() => {
  console.log('🚀 [ProjectTimeline] Component mounted')
  console.log('📍 [ProjectTimeline] Route params:', route.params)
  fetchTimeline()
})
</script>

<style scoped>
.gantt-fullscreen {
  width: 100vw;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: white;
  z-index: 1000;
}

.container {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 8px 0 0 0;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.container :deep(.el-card) {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin: 0;
  border-radius: 0;
  border: none;
  overflow: hidden;
}

.container :deep(.el-card__body) {
  flex: 1;
  padding: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.container :deep(.el-empty) {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>

