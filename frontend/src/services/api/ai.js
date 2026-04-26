import api from './index'

export default {
  suggestTaskDuration(params) {
    return api.get('/ai/task-duration', { params })
  },

  suggestResources(params) {
    return api.get('/ai/resource-suggestions', { params })
  },

  scanDeadlineRisk(data) {
    return api.post('/ai/deadline-risk-scan', data)
  }
}
