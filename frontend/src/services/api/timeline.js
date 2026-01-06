import api from './index'

export default {
  getProjectTimeline(projectId) {
    return api.get(`/timeline/projects/${projectId}`)
  },
  
  moveTask(taskId, dates) {
    return api.put(`/timeline/tasks/${taskId}/move`, dates)
  },
  
  getCriticalPath(projectId) {
    return api.get(`/timeline/projects/${projectId}/critical-path`)
  },
  
  getProgress(projectId) {
    return api.get(`/timeline/projects/${projectId}/progress`)
  }
}

