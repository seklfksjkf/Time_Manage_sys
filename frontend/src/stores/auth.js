import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import authAPI from '@/services/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('access_token') || null)
  
  const isAuthenticated = computed(() => !!token.value)
  
  const setAuth = (userData, accessToken) => {
    user.value = userData
    token.value = accessToken
    localStorage.setItem('access_token', accessToken)
  }
  
  const clearAuth = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('access_token')
  }
  
  const login = async (username, password) => {
    try {
      console.log('📡 Sending login request...')
      const response = await authAPI.login({ username, password })
      console.log('📥 Login response:', response.data)
      
      if (response.data && response.data.access_token && response.data.user) {
        setAuth(response.data.user, response.data.access_token)
        console.log('✅ Auth state updated:', {
          user: response.data.user,
          token: response.data.access_token.substring(0, 20) + '...'
        })
        return { success: true }
      } else {
        console.error('❌ Invalid response format:', response.data)
        return { success: false, error: 'Invalid response format' }
      }
    } catch (error) {
      console.error('❌ Login error:', error)
      console.error('❌ Error response:', error.response?.data)
      return { success: false, error: error.response?.data?.error || error.message || 'Login failed' }
    }
  }
  
  const register = async (userData) => {
    try {
      const response = await authAPI.register(userData)
      return { success: true, data: response.data }
    } catch (error) {
      return { success: false, error: error.response?.data?.error || 'Registration failed' }
    }
  }
  
  const logout = () => {
    clearAuth()
  }
  
  const checkAuth = async () => {
    if (!token.value) return
    
    try {
      const response = await authAPI.getProfile()
      user.value = response.data.user
    } catch (error) {
      clearAuth()
    }
  }
  
  const updateProfile = async (userData) => {
    try {
      const response = await authAPI.updateProfile(userData)
      user.value = response.data.user
      return { success: true }
    } catch (error) {
      return { success: false, error: error.response?.data?.error || 'Update failed' }
    }
  }
  
  return {
    user,
    token,
    isAuthenticated,
    login,
    register,
    logout,
    checkAuth,
    updateProfile
  }
})

