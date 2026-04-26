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
              <el-table-column label="Assigned To" width="180">
                <template #default="scope">
                  <div v-if="scope.row.assigned_to_names && scope.row.assigned_to_names.length > 0">
                    <el-tag
                      v-for="(name, index) in scope.row.assigned_to_names"
                      :key="index"
                      size="small"
                      type="info"
                      style="margin-right: 4px; margin-bottom: 2px;"
                    >
                      {{ name }}
                    </el-tag>
                  </div>
                  <span v-else-if="scope.row.assigned_to_name" class="text-gray">
                    {{ scope.row.assigned_to_name }}
                  </span>
                  <span v-else class="text-gray">Unassigned</span>
                </template>
              </el-table-column>
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
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>Team Members ({{ members.length }})</span>
                <el-button type="primary" size="small" @click="openAddMemberDialog">
                  <el-icon><Plus /></el-icon>
                  Add
                </el-button>
              </div>
            </template>
            <div class="member-list">
              <div v-for="member in members" :key="member.id" class="member-item">
                <el-avatar :size="32">{{ getInitials(member.user_name) }}</el-avatar>
                <span>{{ member.user_name }}</span>
                <el-tag size="small">{{ member.role }}</el-tag>
                <el-button
                  v-if="member.role !== 'owner'"
                  type="danger"
                  size="small"
                  text
                  @click="handleRemoveMember(member)"
                  :title="'Remove member'"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </el-card>

          <el-card class="history-card" style="margin-top: 20px;">
            <template #header>
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>Version History</span>
                <div style="display: flex; gap: 8px; align-items: center;">
                  <el-button size="small" @click="handleRiskScan" :loading="aiLoadingRiskScan">
                    Risk Scan
                  </el-button>
                  <el-button size="small" @click="loadVersionHistory" :loading="historyLoading">
                    <el-icon><Refresh /></el-icon>
                  </el-button>
                </div>
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
                <el-select
                  v-model="newTask.assigned_to"
                  multiple
                  collapse-tags
                  collapse-tags-tooltip
                  placeholder="Select assignees"
                  style="width: 100%"
                >
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

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Estimated Duration (days)">
                <div style="display: flex; gap: 8px; width: 100%;">
                  <el-input-number v-model="newTask.estimated_duration" :min="1" style="flex: 1;" />
                  <el-button @click="handleSuggestDuration" :loading="aiLoadingDuration">AI Suggest</el-button>
                </div>
              </el-form-item>
            </el-col>

            <el-col :span="12">
              <el-form-item label="AI Assignee Suggestion">
                <el-button @click="handleSuggestAssignees" :loading="aiLoadingAssignees" style="width: 100%;">Suggest Members</el-button>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
        
        <template #footer>
          <el-button @click="showTaskDialog = false">Cancel</el-button>
          <el-button type="primary" @click="handleCreateTask">Create</el-button>
        </template>
      </el-dialog>

      <!-- Add Member Dialog -->
      <el-dialog v-model="showAddMemberDialog" title="Add Team Member" width="400px">
        <el-form label-position="top">
          <el-form-item label="Select User">
            <el-select
              v-model="selectedUserId"
              filterable
              placeholder="Search and select a user"
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
          
          <el-form-item label="Role">
            <el-select v-model="newMemberRole" style="width: 100%">
              <el-option label="Member" value="member" />
              <el-option label="Manager" value="manager" />
            </el-select>
          </el-form-item>
        </el-form>
        
        <template #footer>
          <el-button @click="showAddMemberDialog = false">Cancel</el-button>
          <el-button type="primary" @click="handleAddMember" :disabled="!selectedUserId">Add</el-button>
        </template>
      </el-dialog>
    </div>
  </main-layout>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MainLayout from '@/components/Layout/MainLayout.vue'
import projectAPI from '@/services/api/projects'
import taskAPI from '@/services/api/tasks'
import aiAPI from '@/services/api/ai'
import authAPI from '@/services/api/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Calendar, Plus, Document, Delete, Refresh } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const project = ref(null)
const tasks = ref([])
const members = ref([])
const versionHistory = ref([])
const historyLoading = ref(false)
const showTaskDialog = ref(false)
const showAddMemberDialog = ref(false)
const users = ref([])
const selectedUserId = ref(null)
const newMemberRole = ref('member')
const loadingUsers = ref(false)

const aiLoadingDuration = ref(false)
const aiLoadingAssignees = ref(false)
const aiLoadingRiskScan = ref(false)

const newTask = reactive({
  title: '',
  description: '',
  start_date: null,
  end_date: null,
  priority: 'medium',
  assigned_to: [],
  estimated_duration: null
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

// Get IDs of existing project members
const existingMemberIds = computed(() => {
  return members.value.map(m => m.user_id)
})

// Filter users who are not already project members
const availableUsers = computed(() => {
  return users.value.filter(user => !existingMemberIds.value.includes(user.id))
})

// Fetch all users
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

// Handle add member dialog open
const openAddMemberDialog = () => {
  showAddMemberDialog.value = true
  fetchUsers()
  selectedUserId.value = null
  newMemberRole.value = 'member'
}

// Handle add member
const handleAddMember = async () => {
  if (!selectedUserId.value) {
    ElMessage.warning('Please select a user')
    return
  }

  try {
    await projectAPI.addMember(route.params.id, {
      user_id: selectedUserId.value,
      role: newMemberRole.value
    })
    ElMessage.success('Member added successfully')
    showAddMemberDialog.value = false
    fetchMembers()
    selectedUserId.value = null
    newMemberRole.value = 'member'
  } catch (error) {
    console.error('Failed to add member:', error)
    ElMessage.error(error.response?.data?.error || 'Failed to add member')
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

const formatHistoryChanges = (changes) => {
  if (!changes) return 'No details'
  if (typeof changes === 'string') {
    try {
      changes = JSON.parse(changes)
    } catch {
      return changes
    }
  }
  if (changes.title) {
    return changes.title
  }
  return JSON.stringify(changes)
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
    assigned_to: newTask.assigned_to.length > 0 ? newTask.assigned_to : null,
    estimated_duration: newTask.estimated_duration
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
      assigned_to: [],
      estimated_duration: null
    })
  } catch (error) {
    ElMessage.error('Failed to create task')
  }
}

const handleSuggestDuration = async () => {
  if (!newTask.title) {
    ElMessage.warning('Please enter task title first')
    return
  }
  aiLoadingDuration.value = true
  try {
    const res = await aiAPI.suggestTaskDuration({
      project_id: Number(route.params.id),
      title: newTask.title,
      priority: newTask.priority
    })
    newTask.estimated_duration = res.data.suggested_days
  } catch (e) {
    ElMessage.error('Failed to get AI duration suggestion')
  } finally {
    aiLoadingDuration.value = false
  }
}

const handleSuggestAssignees = async () => {
  aiLoadingAssignees.value = true
  try {
    const res = await aiAPI.suggestResources({
      project_id: Number(route.params.id),
      start_date: newTask.start_date ? newTask.start_date.toISOString() : undefined,
      end_date: newTask.end_date ? newTask.end_date.toISOString() : undefined
    })
    const suggestions = res.data.suggestions || []
    if (suggestions.length === 0) {
      ElMessage.info('No suggestions available')
      return
    }
    // pick the lowest workload member
    const best = suggestions[0]
    newTask.assigned_to = [best.user_id]
  } catch (e) {
    ElMessage.error('Failed to get AI assignee suggestions')
  } finally {
    aiLoadingAssignees.value = false
  }
}

const handleRiskScan = async () => {
  aiLoadingRiskScan.value = true
  try {
    const res = await aiAPI.scanDeadlineRisk({ project_id: Number(route.params.id) })
    ElMessage.success(`Risk scan completed: ${res.data.notifications_created} notifications created`)
  } catch (e) {
    ElMessage.error('Failed to run risk scan')
  } finally {
    aiLoadingRiskScan.value = false
  }
}

const handleRemoveMember = async (member) => {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to remove ${member.user_name} from the project?`,
      'Remove Member',
      {
        confirmButtonText: 'Remove',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
    )
    
    await projectAPI.removeMember(route.params.id, member.id)
    ElMessage.success(`${member.user_name} has been removed from the project`)
    fetchMembers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to remove member:', error)
      ElMessage.error(error.response?.data?.error || 'Failed to remove member')
    }
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

.text-gray {
  color: #909399;
}
</style>

