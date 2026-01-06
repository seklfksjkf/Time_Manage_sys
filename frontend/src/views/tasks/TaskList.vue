<template>
  <main-layout>
    <div class="container">
      <div class="page-header">
        <h2 class="page-title">My Tasks</h2>
        <el-select v-model="statusFilter" placeholder="Filter by status" style="width: 200px">
          <el-option label="All Tasks" value="" />
          <el-option label="Pending" value="pending" />
          <el-option label="In Progress" value="in_progress" />
          <el-option label="Completed" value="completed" />
          <el-option label="Blocked" value="blocked" />
        </el-select>
      </div>

      <el-table :data="filteredTasks" style="width: 100%">
        <el-table-column prop="title" label="Task" min-width="200" />
        
        <el-table-column prop="project_id" label="Project" width="150">
          <template #default="scope">
            <span>Project #{{ scope.row.project_id }}</span>
          </template>
        </el-table-column>
        
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
        
        <el-table-column prop="start_date" label="Start Date" width="120">
          <template #default="scope">
            {{ formatDate(scope.row.start_date) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="end_date" label="Due Date" width="120">
          <template #default="scope">
            {{ formatDate(scope.row.end_date) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="progress" label="Progress" width="150">
          <template #default="scope">
            <el-progress :percentage="scope.row.progress" />
          </template>
        </el-table-column>
        
        <el-table-column label="Actions" width="100" fixed="right">
          <template #default="scope">
            <el-button
              type="primary"
              size="small"
              text
              @click="editTask(scope.row)"
            >
              Edit
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Edit Task Dialog -->
      <el-dialog v-model="showEditDialog" title="Update Task" width="500px">
        <el-form v-if="editingTask" :model="editingTask" label-position="top">
          <el-form-item label="Status">
            <el-select v-model="editingTask.status" style="width: 100%">
              <el-option label="Pending" value="pending" />
              <el-option label="In Progress" value="in_progress" />
              <el-option label="Completed" value="completed" />
              <el-option label="Blocked" value="blocked" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="Progress">
            <el-slider v-model="editingTask.progress" :show-tooltip="true" />
          </el-form-item>
        </el-form>
        
        <template #footer>
          <el-button @click="showEditDialog = false">Cancel</el-button>
          <el-button type="primary" @click="handleUpdate">Update</el-button>
        </template>
      </el-dialog>
    </div>
  </main-layout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import MainLayout from '@/components/Layout/MainLayout.vue'
import dashboardAPI from '@/services/api/dashboard'
import taskAPI from '@/services/api/tasks'
import { ElMessage } from 'element-plus'

const tasks = ref([])
const statusFilter = ref('')
const showEditDialog = ref(false)
const editingTask = ref(null)

const filteredTasks = computed(() => {
  if (!statusFilter.value) return tasks.value
  return tasks.value.filter(task => task.status === statusFilter.value)
})

const fetchTasks = async () => {
  try {
    const response = await dashboardAPI.getMyTasks()
    tasks.value = response.data.tasks
  } catch (error) {
    ElMessage.error('Failed to load tasks')
  }
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString()
}

const editTask = (task) => {
  editingTask.value = { ...task }
  showEditDialog.value = true
}

const handleUpdate = async () => {
  try {
    await taskAPI.update(editingTask.value.id, {
      status: editingTask.value.status,
      progress: editingTask.value.progress
    })
    ElMessage.success('Task updated successfully')
    showEditDialog.value = false
    fetchTasks()
  } catch (error) {
    ElMessage.error('Failed to update task')
  }
}

onMounted(() => {
  fetchTasks()
})
</script>

<style scoped>
/* Use global styles */
</style>

