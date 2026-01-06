import { defineStore } from 'pinia'
import { ref } from 'vue'
import taskAPI from '@/services/api/tasks'

export const useTaskStore = defineStore('tasks', () => {
  const tasks = ref([])
  const currentTask = ref(null)
  const loading = ref(false)
  
  const fetchTasks = async (params = {}) => {
    loading.value = true
    try {
      const response = await taskAPI.getAll(params)
      tasks.value = response.data.tasks
    } catch (error) {
      console.error('Failed to fetch tasks:', error)
    } finally {
      loading.value = false
    }
  }
  
  const fetchTask = async (id) => {
    try {
      const response = await taskAPI.getById(id)
      currentTask.value = response.data.task
      return currentTask.value
    } catch (error) {
      console.error('Failed to fetch task:', error)
      return null
    }
  }
  
  const createTask = async (taskData) => {
    try {
      const response = await taskAPI.create(taskData)
      tasks.value.unshift(response.data.task)
      return { success: true, task: response.data.task }
    } catch (error) {
      return { success: false, error: error.response?.data?.error || 'Failed to create task' }
    }
  }
  
  const updateTask = async (id, taskData) => {
    try {
      const response = await taskAPI.update(id, taskData)
      const index = tasks.value.findIndex(t => t.id === id)
      if (index !== -1) {
        tasks.value[index] = response.data.task
      }
      if (currentTask.value?.id === id) {
        currentTask.value = response.data.task
      }
      return { success: true }
    } catch (error) {
      return { success: false, error: error.response?.data?.error || 'Failed to update task' }
    }
  }
  
  const deleteTask = async (id) => {
    try {
      await taskAPI.delete(id)
      tasks.value = tasks.value.filter(t => t.id !== id)
      if (currentTask.value?.id === id) {
        currentTask.value = null
      }
      return { success: true }
    } catch (error) {
      return { success: false, error: error.response?.data?.error || 'Failed to delete task' }
    }
  }
  
  return {
    tasks,
    currentTask,
    loading,
    fetchTasks,
    fetchTask,
    createTask,
    updateTask,
    deleteTask
  }
})

