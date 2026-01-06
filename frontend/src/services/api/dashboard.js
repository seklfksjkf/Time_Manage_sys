import api from './index'

export default {
  getOverview() {
    return api.get('/dashboard/overview')
  },
  
  getMyTasks(params) {
    return api.get('/dashboard/my-tasks', { params })
  },
  
  getStatistics() {
    return api.get('/dashboard/statistics')
  }
}

