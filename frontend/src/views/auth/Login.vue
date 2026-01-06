<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h1>Time Management System</h1>
        <p>Login to your account</p>
      </div>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="rules"
        class="auth-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="Username"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="Password"
            size="large"
            :prefix-icon="Lock"
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleLogin"
            style="width: 100%"
          >
            Login
          </el-button>
        </el-form-item>
      </el-form>

      <div class="auth-footer">
        <span>Don't have an account?</span>
        <router-link to="/register">Register</router-link>
      </div>

      <div class="demo-credentials">
        <p><strong>Demo Accounts:</strong></p>
        <p>Admin: admin / admin123</p>
        <p>Manager: john_doe / password123</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const loginFormRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: 'Please enter username', trigger: 'blur' }],
  password: [{ required: true, message: 'Please enter password', trigger: 'blur' }]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      console.log('🔐 Attempting login...')
      const result = await authStore.login(loginForm.username, loginForm.password)
      
      console.log('📝 Login result:', result)
      console.log('🔑 Auth store state:', {
        isAuthenticated: authStore.isAuthenticated,
        token: !!authStore.token,
        user: authStore.user
      })

      if (result.success) {
        ElMessage.success('Login successful')
        console.log('✅ Login successful, redirecting to dashboard...')
        
        // Small delay to ensure token is saved to localStorage
        await new Promise(resolve => setTimeout(resolve, 100))
        
        // Verify token is saved
        const savedToken = localStorage.getItem('access_token')
        console.log('🔍 Verifying saved token:', {
          hasSavedToken: !!savedToken,
          token: savedToken ? savedToken.substring(0, 30) + '...' : 'none'
        })
        
        // Use router.replace instead of router.push to avoid keeping login in history
        await router.replace('/dashboard')
        console.log('✅ Navigation completed')
      } else {
        console.error('❌ Login failed:', result.error)
        ElMessage.error(result.error || 'Login failed')
      }
    } catch (error) {
      console.error('❌ Login error:', error)
      ElMessage.error('An unexpected error occurred')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

.auth-container::before {
  content: '';
  position: absolute;
  width: 500px;
  height: 500px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  top: -200px;
  left: -200px;
  animation: float 6s ease-in-out infinite;
}

.auth-container::after {
  content: '';
  position: absolute;
  width: 400px;
  height: 400px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 50%;
  bottom: -150px;
  right: -150px;
  animation: float 8s ease-in-out infinite reverse;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-30px); }
}

.auth-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 48px;
  width: 100%;
  max-width: 480px;
  box-shadow: 0 30px 90px rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.3);
  position: relative;
  z-index: 1;
  animation: slideUp 0.6s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.auth-header {
  text-align: center;
  margin-bottom: 40px;
}

.auth-header h1 {
  font-size: 32px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 12px;
  letter-spacing: -0.5px;
}

.auth-header p {
  color: #606266;
  font-size: 15px;
}

.auth-form {
  margin-top: 32px;
}

:deep(.el-form-item) {
  margin-bottom: 24px;
}

:deep(.el-input__wrapper) {
  border-radius: 12px;
  padding: 12px 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

:deep(.el-button--large) {
  border-radius: 12px;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.5px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s ease;
}

:deep(.el-button--large:hover) {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
}

.auth-footer {
  text-align: center;
  margin-top: 28px;
  color: #606266;
  font-size: 14px;
}

.auth-footer a {
  color: #667eea;
  text-decoration: none;
  margin-left: 8px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.auth-footer a:hover {
  color: #764ba2;
  text-decoration: underline;
}

.demo-credentials {
  margin-top: 32px;
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
  border-radius: 16px;
  font-size: 13px;
  color: #606266;
  text-align: center;
  border: 1px solid rgba(102, 126, 234, 0.1);
}

.demo-credentials p {
  margin: 6px 0;
  line-height: 1.6;
}

.demo-credentials strong {
  color: #303133;
  font-weight: 700;
}
</style>

