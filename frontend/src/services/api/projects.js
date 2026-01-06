import api from './index'

export default {
  getAll() {
    return api.get('/projects')
  },
  
  getById(id) {
    return api.get(`/projects/${id}`)
  },
  
  create(projectData) {
    return api.post('/projects', projectData)
  },
  
  update(id, projectData) {
    return api.put(`/projects/${id}`, projectData)
  },
  
  delete(id) {
    return api.delete(`/projects/${id}`)
  },
  
  getMembers(id) {
    return api.get(`/projects/${id}/members`)
  },
  
  addMember(id, memberData) {
    return api.post(`/projects/${id}/members`, memberData)
  },
  
  removeMember(projectId, memberId) {
    return api.delete(`/projects/${projectId}/members/${memberId}`)
  },
  
  getVersionHistory(id) {
    return api.get(`/projects/${id}/version-history`)
  }
}

