<template>
  <main-layout>
    <div class="container">
      <h2 class="page-title">Profile Settings</h2>

      <el-card>
        <el-form :model="profileForm" label-position="top" style="max-width: 600px">
          <el-form-item label="Username">
            <el-input v-model="profileForm.username" disabled />
          </el-form-item>
          
          <el-form-item label="Email">
            <el-input v-model="profileForm.email" />
          </el-form-item>
          
          <el-form-item label="Full Name">
            <el-input v-model="profileForm.full_name" />
          </el-form-item>
          
          <el-form-item label="Role">
            <el-tag>{{ profileForm.role }}</el-tag>
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="handleUpdate">
              Update Profile
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </main-layout>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import MainLayout from '@/components/Layout/MainLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()

const profileForm = reactive({
  username: '',
  email: '',
  full_name: '',
  role: ''
})

const loadProfile = () => {
  if (authStore.user) {
    Object.assign(profileForm, authStore.user)
  }
}

const handleUpdate = async () => {
  const result = await authStore.updateProfile({
    email: profileForm.email,
    full_name: profileForm.full_name
  })
  
  if (result.success) {
    ElMessage.success('Profile updated successfully')
  } else {
    ElMessage.error(result.error)
  }
}

onMounted(() => {
  loadProfile()
})
</script>

