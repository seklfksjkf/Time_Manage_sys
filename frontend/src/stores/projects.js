import { defineStore } from 'pinia'
import { ref } from 'vue'
import projectAPI from '@/services/api/projects'

export const useProjectStore = defineStore('projects', () => {
  const projects = ref([])
  const currentProject = ref(null)
  const loading = ref(false)
  
  const fetchProjects = async () => {
    loading.value = true
    try {
      const response = await projectAPI.getAll()
      projects.value = response.data.projects
    } catch (error) {
      console.error('Failed to fetch projects:', error)
    } finally {
      loading.value = false
    }
  }
  
  const fetchProject = async (id) => {
    loading.value = true
    try {
      const response = await projectAPI.getById(id)
      currentProject.value = response.data.project
      return currentProject.value
    } catch (error) {
      console.error('Failed to fetch project:', error)
      return null
    } finally {
      loading.value = false
    }
  }
  
  const createProject = async (projectData) => {
    try {
      const response = await projectAPI.create(projectData)
      projects.value.unshift(response.data.project)
      return { success: true, project: response.data.project }
    } catch (error) {
      return { success: false, error: error.response?.data?.error || 'Failed to create project' }
    }
  }
  
  const updateProject = async (id, projectData) => {
    try {
      const response = await projectAPI.update(id, projectData)
      const index = projects.value.findIndex(p => p.id === id)
      if (index !== -1) {
        projects.value[index] = response.data.project
      }
      if (currentProject.value?.id === id) {
        currentProject.value = response.data.project
      }
      return { success: true }
    } catch (error) {
      return { success: false, error: error.response?.data?.error || 'Failed to update project' }
    }
  }
  
  const deleteProject = async (id) => {
    try {
      await projectAPI.delete(id)
      projects.value = projects.value.filter(p => p.id !== id)
      if (currentProject.value?.id === id) {
        currentProject.value = null
      }
      return { success: true }
    } catch (error) {
      return { success: false, error: error.response?.data?.error || 'Failed to delete project' }
    }
  }
  
  return {
    projects,
    currentProject,
    loading,
    fetchProjects,
    fetchProject,
    createProject,
    updateProject,
    deleteProject
  }
})

