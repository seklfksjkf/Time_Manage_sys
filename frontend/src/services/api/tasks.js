import api from './index'

export default {
  getAll(params) {
    return api.get('/tasks', { params })
  },
  
  getById(id) {
    return api.get(`/tasks/${id}`)
  },
  
  create(taskData) {
    return api.post('/tasks', taskData)
  },
  
  update(id, taskData) {
    return api.put(`/tasks/${id}`, taskData)
  },
  
  delete(id) {
    return api.delete(`/tasks/${id}`)
  },
  
  getDependencies(id) {
    return api.get(`/tasks/${id}/dependencies`)
  },
  
  addDependency(id, dependencyData) {
    return api.post(`/tasks/${id}/dependencies`, dependencyData)
  },
  
  removeDependency(taskId, dependencyId) {
    return api.delete(`/tasks/${taskId}/dependencies/${dependencyId}`)
  },
  
  getComments(id) {
    return api.get(`/tasks/${id}/comments`)
  },
  
  addComment(id, commentData) {
    return api.post(`/tasks/${id}/comments`, commentData)
  }
}

